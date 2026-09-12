"""Video jobs and continuous public-YouTube capture. All work is account scoped."""

import json
import math
import os
import re
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import imageio_ffmpeg

from .agent import Agent
from .config import DATA, MAX_UPLOAD
from .observability import record, span, trace_reference
from .provider import Gemini
from .store import Store


class Cancelled(Exception):
    pass


def youtube(value):
    u = urlparse(value)
    if u.scheme != "https" or u.username or u.password:
        raise ValueError("Use a public HTTPS YouTube video URL.")
    if u.hostname == "youtu.be":
        id = u.path.strip("/")
    elif u.hostname in ["youtube.com", "www.youtube.com", "m.youtube.com"]:
        id = parse_qs(u.query).get("v", [""])[0] or (
            u.path.split("/")[-1]
            if u.path.startswith(("/live/", "/embed/", "/shorts/"))
            else ""
        )
    else:
        raise ValueError("Only public YouTube URLs are supported.")
    if not re.fullmatch(r"[\w-]{11}", id):
        raise ValueError("Invalid YouTube video ID.")
    return "https://www.youtube.com/watch?v=" + id


def interval(start, end, cutoff):
    if (
        not all(
            isinstance(v, (int, float)) and math.isfinite(v)
            for v in [start, end, cutoff]
        )
        or not 0 <= start < end <= cutoff <= 604800
    ):
        raise ValueError("Use a valid interval at or before the spoiler cutoff.")
    if end - start > 3600:
        raise ValueError("Analyze up to one hour per job; split longer requests.")


def ffmpeg():
    return os.environ.get("FFMPEG_BINARY") or imageio_ffmpeg.get_ffmpeg_exe()


def duration(path):
    r = subprocess.run(
        [ffmpeg(), "-hide_banner", "-i", str(path)], capture_output=True, timeout=20
    )
    match = re.search(rb"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not match:
        raise ValueError(
            "Unable to read the uploaded video duration. Use a valid MP4, MOV or WebM."
        )
    h, m, s = map(float, match.groups())
    return h * 3600 + m * 60 + s


class Service:
    def __init__(self, store=None, provider_factory=Gemini):
        self.store = store or Store()
        self.factory = provider_factory

    def add_video(self, owner, title, url="", upload=None, filename=""):
        if not 1 <= len(title.strip()) <= 180:
            raise ValueError("Enter a title of up to 180 characters.")
        id = str(uuid.uuid4())
        media = {
            "id": id,
            "title": title.strip(),
            "url": "",
            "path": "",
            "duration": 604800,
            "kind": "recorded",
            "embedding_model": os.environ.get(
                "GEMINI_EMBED_MODEL", "gemini-embedding-2"
            ),
        }
        if upload is not None:
            if not 0 < len(upload) <= MAX_UPLOAD:
                raise ValueError("Upload a video of up to 100 MB.")
            ext = Path(filename).suffix.lower()
            if ext not in {".mp4", ".mov", ".webm"}:
                raise ValueError("Use MP4, MOV or WebM.")
            folder = DATA / "uploads" / owner
            folder.mkdir(parents=True, exist_ok=True, mode=0o700)
            path = folder / (id + ext)
            # Bound total retained uploads per account.
            if (
                sum(f.stat().st_size for f in folder.iterdir() if f.is_file())
                + len(upload)
                > 500 * 1024 * 1024
            ):
                raise ValueError("Account upload storage limit reached (500 MB).")
            path.write_bytes(upload)
            try:
                media.update(path=str(path), duration=duration(path))
            except Exception:
                path.unlink(missing_ok=True)
                raise
        else:
            media["url"] = youtube(url)
        self.store.save_media(owner, media)
        return media

    def enqueue(self, owner, kind, payload):
        m = self.store.media(owner, payload["media"])
        interval(payload["start"], payload["end"], payload.get("as_of", payload["end"]))
        if payload["end"] > m["duration"]:
            raise ValueError("The interval exceeds the video duration.")
        if (
            kind == "recap"
            and not 1 <= len(payload.get("question", "").strip()) <= 1000
        ):
            raise ValueError("Enter a question of up to 1000 characters.")
        if kind == "live":
            if not m["url"]:
                raise ValueError("Live capture requires a public YouTube stream URL.")
            if payload["end"] - payload["start"] > 900:
                raise ValueError("Live sessions are limited to 15 minutes each.")
            m["kind"] = "live"
            self.store.save_media(owner, m)
        return self.store.enqueue(owner, kind, payload)

    def inspect(self, owner, job, media_id, start, end, force=False):
        m = self.store.media(owner, media_id)
        provider = self.factory(self.store, owner, job)
        file = None
        uri = m["url"]
        if m["kind"] == "live":
            raise ValueError(
                "Live evidence is processed by capture jobs; unrecorded intervals cannot be reconstructed."
            )
        if m["path"]:
            path = Path(m["path"]).resolve()
            if not path.is_relative_to((DATA / "uploads" / owner).resolve()):
                raise ValueError("Invalid stored media path.")
            if (
                path.suffix.lower() == ".mp4"
                and path.stat().st_size <= 12 * 1024 * 1024
            ):
                uri = path.read_bytes()
            else:
                file = provider.upload(str(path))
                uri = file.uri
        limits = []
        try:
            a = float(start)
            while a < end:
                b = min(a + 300, end)
                if self.store.job(owner, job)["cancel"]:
                    raise Cancelled()
                if not force and [a, b] in self.store.windows(owner, media_id):
                    a = b
                    continue
                events, warnings = provider.extract(uri, a, b)
                vectors = provider.embed([e["text"] for e in events])
                self.store.save_window(owner, media_id, a, b, events, vectors, warnings)
                limits += warnings
                a = b
        finally:
            if file:
                try:
                    provider.client.files.delete(name=file.name)
                except Exception:
                    pass
        return {
            "media": media_id,
            "coverage": self.store.windows(owner, media_id),
            "limitations": limits,
        }

    def recap(self, job, resume=None):
        owner, id = job["owner"], job["id"]
        p = job["payload"]
        provider = self.factory(self.store, owner, id)
        agent = Agent(
            self.store,
            provider,
            owner,
            id,
            lambda media, a, b: self.inspect(owner, id, media, a, b, force=True),
        )
        try:
            return agent.run(
                None if resume else {**p, "iterations": 0, "trace": []}, resume=resume
            )
        finally:
            agent.close()

    def review(self, owner, id, decision):
        if decision not in ["approved", "rejected"]:
            raise ValueError("Choose approved or rejected.")
        job = self.store.job(owner, id)
        with self.store.db() as c:
            changed = c.execute(
                "UPDATE jobs SET status='running',lease=? WHERE id=? AND owner=? AND status='awaiting_review'",
                (time.time() + 180, id, owner),
            ).rowcount
        if changed != 1:
            raise ValueError("This job is not waiting for review.")
        try:
            result, waiting = self.execute(job, resume=decision)
            self.store.finish(
                owner, id, "awaiting_review" if waiting else "completed", result
            )
        except Exception:
            self.store.finish(
                owner,
                id,
                "awaiting_review",
                job["result"],
                error="Review could not be saved. Try again.",
            )
            raise

    def live(self, job):
        owner, id, p = job["owner"], job["id"], job["payload"]
        m = self.store.media(owner, p["media"])
        # yt-dlp handles ordinary public access only. No cookies, auth bypass or proxy rotation.
        r = subprocess.run(
            [
                sys.executable,
                "-m",
                "yt_dlp",
                "--no-playlist",
                "--skip-download",
                "--dump-single-json",
                "-f",
                "best[height<=480][protocol*=m3u8]/best[height<=480]",
                m["url"],
            ],
            capture_output=True,
            timeout=60,
        )
        if r.returncode:
            raise ValueError(
                "YouTube live access failed. Check that the stream is public and active. No access restrictions were bypassed."
            )
        info = json.loads(r.stdout)
        if not info.get("is_live"):
            raise ValueError(
                "This URL is not currently live. Use recorded-video analysis instead."
            )
        stream = info.get("url", "")
        u = urlparse(stream)
        if u.scheme != "https" or not (u.hostname or "").endswith(".googlevideo.com"):
            raise ValueError("Unsupported live media host.")
        folder = DATA / "live" / id
        folder.mkdir(parents=True, exist_ok=True)
        # Capturing continues while completed segments are analyzed. Limit disk use and duration.
        log = open(folder / "capture.log", "wb")
        proc = subprocess.Popen(
            [
                ffmpeg(),
                "-hide_banner",
                "-loglevel",
                "error",
                "-protocol_whitelist",
                "https,tls,tcp,crypto",
                "-i",
                stream,
                "-t",
                str(p["end"] - p["start"]),
                "-map",
                "0:v:0",
                "-map",
                "0:a?",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-b:v",
                "400k",
                "-vf",
                "scale=-2:360",
                "-c:a",
                "aac",
                "-b:a",
                "64k",
                "-force_key_frames",
                "expr:gte(t,n_forced*60)",
                "-f",
                "segment",
                "-segment_time",
                "60",
                "-reset_timestamps",
                "1",
                str(folder / "%04d.mp4"),
            ],
            stdout=subprocess.DEVNULL,
            stderr=log,
        )
        provider = self.factory(self.store, owner, id)
        done = set()
        limitations = []
        deadline = time.monotonic() + (p["end"] - p["start"]) + 300
        try:
            while True:
                if self.store.job(owner, id)["cancel"]:
                    raise Cancelled()
                if time.monotonic() > deadline:
                    raise ValueError("Live capture exceeded its time budget.")
                if (
                    sum(f.stat().st_size for f in folder.glob("*.mp4"))
                    > 100 * 1024 * 1024
                ):
                    raise ValueError("Live capture exceeded its storage budget.")
                files = sorted(folder.glob("*.mp4"))
                finished = proc.poll() is not None
                ready = files if finished else files[:-1]
                for path in ready:
                    if path.name in done:
                        continue
                    origin = p["start"] + int(path.stem) * 60
                    length = min(duration(path), p["end"] - origin)
                    remote = None
                    uri = (
                        path.read_bytes()
                        if path.stat().st_size <= 12 * 1024 * 1024
                        else None
                    )
                    if uri is None:
                        remote = provider.upload(str(path))
                        uri = remote.uri
                    try:
                        events, warnings = provider.extract(
                            uri, 0, length, origin=origin
                        )
                        self.store.save_window(
                            owner,
                            m["id"],
                            origin,
                            origin + length,
                            events,
                            provider.embed([e["text"] for e in events]),
                            warnings,
                        )
                        limitations += warnings
                    finally:
                        try:
                            if remote:
                                provider.client.files.delete(name=remote.name)
                        except Exception:
                            pass
                    done.add(path.name)
                    path.unlink()
                if finished:
                    if proc.returncode or not done:
                        raise ValueError(
                            "Live capture ended with a media error. Successfully processed windows remain available."
                        )
                    break
                time.sleep(1)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
            log.close()
            for f in folder.glob("*.mp4"):
                f.unlink(missing_ok=True)
            # The capture log can contain expiring signed media URLs; never retain it.
            (folder / "capture.log").unlink(missing_ok=True)
        return {
            "media": m["id"],
            "coverage": self.store.windows(owner, m["id"]),
            "limitations": limitations,
            "clock_note": "Live offsets use the elapsed time supplied at capture start; broadcaster/network delay can affect alignment.",
        }

    def execute(self, job, resume=None):
        """Trace a worker attempt or review resume under its durable job ID."""
        with span(
            "RaceTime human review" if resume else "RaceTime video job",
            inputs={**job["payload"], "kind": job["kind"], "review": resume},
            metadata={"job_id": job["id"], "media_id": job["payload"]["media"]},
        ) as run:
            if job["kind"] == "analyze":
                result = self.inspect(
                    job["owner"],
                    job["id"],
                    job["payload"]["media"],
                    job["payload"]["start"],
                    job["payload"]["end"],
                )
                waiting = False
            elif job["kind"] == "live":
                result, waiting = self.live(job), False
            else:
                result, waiting = self.recap(job, resume=resume)
            record(
                run,
                {
                    "status": "awaiting_review" if waiting else "completed",
                    "result": result,
                },
            )
            reference = trace_reference(run)
            if reference:
                result["observability"] = reference
                if resume and (job.get("result") or {}).get("observability"):
                    result["observability"]["original_run"] = job["result"][
                        "observability"
                    ]
            return result, waiting

    def process_one(self):
        job = self.store.claim()
        if not job:
            return False
        stop = threading.Event()

        def heartbeat():
            while not stop.wait(20):
                self.store.heartbeat(job["id"])

        beat = threading.Thread(target=heartbeat, daemon=True)
        beat.start()
        try:
            result, waiting = self.execute(job)
            if self.store.job(job["owner"], job["id"])["cancel"]:
                raise Cancelled()
            self.store.finish(
                job["owner"],
                job["id"],
                "awaiting_review" if waiting else "completed",
                result,
            )
        except Cancelled:
            self.store.finish(job["owner"], job["id"], "cancelled")
        except Exception as exc:
            # Deliberate ValueErrors contain safe user messages; SDK/process internals may include secrets.
            self.store.finish(
                job["owner"],
                job["id"],
                "failed",
                error=str(exc)[:600]
                if isinstance(exc, ValueError)
                else "Job failed. Check provider access or source availability and retry.",
            )
        finally:
            stop.set()
            beat.join(timeout=1)
        return True
