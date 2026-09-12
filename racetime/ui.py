"""Small account-backed video workspace for the primary Streamlit app."""

import json
import os
from pathlib import Path

import streamlit as st

from demo.client import clock, elapsed

from .config import DATA, configured
from .service import Service


@st.cache_resource
def service():
    return Service()


def render():
    svc = service()
    store = svc.store
    st.title("Ask your race video")
    st.caption("Choose an interval, inspect the evidence, and review the recap.")
    if not configured():
        st.info(
            "Video analysis needs GEMINI_API_KEY in the project .env file. Setup steps are in docs/setup.md. The evidence demo works without a key."
        )
    if (
        os.getenv("RACETIME_PUBLIC") == "true"
        or os.getenv("RACETIME_AUTH_MODE") == "oidc"
    ):
        # Public access fails closed until a verified OIDC account is allow-listed.
        try:
            if not st.user.is_logged_in:
                if st.button("Sign in with Google"):
                    st.login()
                return
            allowed = {
                e.strip().lower()
                for e in os.getenv("RACETIME_ALLOWED_EMAILS", "").split(",")
                if e.strip()
            }
            if (
                not st.user.get("email_verified")
                or st.user.get("email", "").lower() not in allowed
            ):
                st.error("This account has not been granted access.")
                if st.button("Sign out"):
                    st.logout()
                return
            import hashlib

            st.session_state.video_user = hashlib.sha256(
                (str(st.user.get("iss", "google")) + ":" + str(st.user["sub"])).encode()
            ).hexdigest()
        except (KeyError, RuntimeError):
            st.error(
                "Public sign-in is not configured. Follow docs/setup.md before exposing the app."
            )
            return
    if "video_user" not in st.session_state:
        with st.form("video_login"):
            mode = st.selectbox("Account action", ["Sign in", "Create account"])
            name = st.text_input("Username", max_chars=40)
            password = st.text_input(
                "Password (at least 12 characters)", type="password", max_chars=256
            )
            submit = st.form_submit_button("Continue")
        if submit:
            try:
                if mode == "Create account":
                    store.register(name, password)
                st.session_state.video_user = store.login(name, password)
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
        st.caption(
            "Your account restores videos and jobs after a refresh. Passwords are salted and hashed locally. Keep your password; email recovery is not configured."
        )
        return
    owner = st.session_state.video_user
    if st.sidebar.button("Sign out of video workspace"):
        st.session_state.pop("video_user")
        if (
            os.getenv("RACETIME_AUTH_MODE") == "oidc"
            or os.getenv("RACETIME_PUBLIC") == "true"
        ):
            st.logout()
        st.rerun()
    usage = store.usage(owner)
    st.sidebar.caption(
        f"Last 24 hours: {usage['calls']} provider calls · {usage['input_tokens']} input / {usage['output_tokens']} output generation tokens. Upload and embedding token charges may be additional; provider billing is authoritative."
    )
    add, ask, jobs, review = st.tabs(
        ["Videos", "Ask / inspect", "Jobs / results", "Evaluation"]
    )
    with add:
        with st.form("video_add"):
            title = st.text_input("Video title", max_chars=180)
            url = st.text_input("Public YouTube URL")
            upload = st.file_uploader(
                "Or upload MP4, MOV or WebM (100 MB maximum)",
                type=["mp4", "mov", "webm"],
                key="video_upload",
            )
            saved = st.form_submit_button("Save video")
        if saved:
            try:
                svc.add_video(
                    owner,
                    title,
                    url,
                    upload.getvalue() if upload else None,
                    upload.name if upload else "",
                )
                st.success("Video saved. Select it under Ask / inspect.")
            except (ValueError, TimeoutError) as exc:
                st.error(str(exc))
        media = store.all_media(owner)
        for m in media:
            with st.expander(m["title"]):
                st.write("Analyzed windows:", store.windows(owner, m["id"]))
                if m["url"]:
                    st.video(m["url"])
                elif Path(m["path"]).exists():
                    st.video(m["path"])
    media = store.all_media(owner)
    with ask:
        if not media:
            st.write("Save a video first.")
        else:
            by_id = {m["id"]: m for m in media}
            selected = st.selectbox(
                "Video", list(by_id), format_func=lambda id: by_id[id]["title"]
            )
            action = st.selectbox(
                "Action",
                ["Ask the agent", "Inspect an interval", "Capture a live stream"],
            )
            latest = (
                st.checkbox(
                    "Use the last 15 minutes of processed live coverage", value=False
                )
                if by_id[selected]["kind"] == "live" and action == "Ask the agent"
                else False
            )
            with st.form("video_question"):
                a, b, c = st.columns(3)
                start = a.text_input("Start / current live elapsed time", value="00:00")
                end = b.text_input("End", value="05:00")
                cutoff = c.text_input("Spoiler cutoff", value="05:00")
                question = st.text_input(
                    "Question",
                    value="What happened?",
                    max_chars=1000,
                    help="For example: What happened between 10:00 and 15:00? Set Start and End to match; times in the question do not change those fields.",
                )
                if action == "Ask the agent" and not latest:
                    st.caption(
                        "Example: What happened between 10:00 and 15:00? Set Start to 10:00, End to 15:00 and Spoiler cutoff to 15:00."
                    )
                if action == "Capture a live stream":
                    st.caption(
                        "Capture starts at the current live edge for up to 15 minutes. Enter the broadcast’s current elapsed time as Start. Processing continues in the background; older unrecorded footage is not available automatically."
                    )
                submit = st.form_submit_button("Queue job", disabled=not configured())
            if submit:
                try:
                    kind = {
                        "Ask the agent": "recap",
                        "Inspect an interval": "analyze",
                        "Capture a live stream": "live",
                    }[action]
                    start_s, end_s, cutoff_s = (
                        elapsed(start),
                        elapsed(end),
                        elapsed(cutoff),
                    )
                    if latest:
                        windows = store.windows(owner, selected)
                        if not windows:
                            raise ValueError(
                                "No live segments have finished processing yet."
                            )
                        end_s = max(w[1] for w in windows)
                        start_s = max(min(w[0] for w in windows), end_s - 900)
                        cutoff_s = end_s
                    id = svc.enqueue(
                        owner,
                        kind,
                        {
                            "media": selected,
                            "start": start_s,
                            "end": end_s,
                            "as_of": cutoff_s,
                            "question": question,
                        },
                    )
                    st.success("Job queued. Open Jobs / results to follow progress.")
                except ValueError as exc:
                    st.error(str(exc))
    with jobs:
        st.button("Refresh jobs")
        for j in store.jobs(owner):
            with st.expander(
                f"{j['kind']} · {j['status']} · {j['id'][:8]}",
                expanded=j["status"] == "awaiting_review",
            ):
                p = j["payload"]
                st.caption(
                    f"{clock(p['start'])}–{clock(p['end'])} · {p.get('question', '')}"
                )
                if j["error"]:
                    st.error(j["error"])
                if j["status"] in ["queued", "running"]:
                    if st.button("Cancel job", key="cancel-" + j["id"]):
                        store.cancel(owner, j["id"])
                        st.rerun()
                result = j["result"] or {}
                observability = result.get("observability", {})
                if observability.get("url"):
                    st.link_button("Open LangSmith trace", observability["url"])
                    st.caption(
                        "Trace delivery is asynchronous; quota or connection errors can prevent ingestion."
                    )
                if result.get("gaps"):
                    st.warning(
                        "No processed coverage for these intervals (seconds): "
                        + str(result["gaps"])
                    )
                for note in result.get("limitations", []):
                    st.warning(note)
                events = {e["id"]: e for e in result.get("selected", [])}
                m = store.media(owner, p["media"])
                for sentence in result.get("narrative", {}).get("sentences", []):
                    st.write(sentence["text"])
                    for id in sentence["evidence_ids"]:
                        e = events[id]
                        if m["url"]:
                            st.link_button(
                                clock(e["start"]) + " · " + id,
                                m["url"] + "&t=" + str(int(e["start"])),
                            )
                        else:
                            st.caption(clock(e["start"]) + " · " + id)
                            if st.button(
                                "Play evidence",
                                key=j["id"] + id + sentence["text"][:20],
                            ):
                                st.video(m["path"], start_time=int(e["start"]))
                if result.get("clarification"):
                    st.warning(result["clarification"])
                if result.get("narrative", {}).get("warning"):
                    st.warning(result["narrative"]["warning"])
                if j["status"] == "awaiting_review":
                    a, b = st.columns(2)
                    for col, decision in [(a, "approved"), (b, "rejected")]:
                        if col.button(decision.title(), key=decision + j["id"]):
                            try:
                                svc.review(owner, j["id"], decision)
                                st.rerun()
                            except ValueError as exc:
                                st.error(str(exc))
                if result:
                    st.json(result, expanded=False)
                    st.download_button(
                        "Export result",
                        json.dumps(result, indent=2),
                        j["id"] + ".json",
                        key="export-" + j["id"],
                    )
    with review:
        st.write(
            "Create independently reviewed examples from real race footage. Model-generated observations are not ground truth."
        )
        candidates = [
            j for j in store.jobs(owner) if j["kind"] == "recap" and j["result"]
        ]
        if candidates:
            by_id = {j["id"]: j for j in candidates}
            id = st.selectbox("Result to evaluate", list(by_id))
            with st.form("ground_truth"):
                watched = st.checkbox(
                    "I independently watched this interval and checked the source timestamps."
                )
                facts = st.text_area("Expected facts, one per line")
                accuracy = st.slider("Supported summary sentences (%)", 0, 100, 0)
                missed = st.number_input("Important events missed", 0, 100, 0)
                leaks = st.number_input(
                    "Facts from after the spoiler cutoff", 0, 100, 0
                )
                timestamp_error = st.number_input(
                    "Largest timestamp error (seconds)", 0.0, 3600.0, 0.0
                )
                save = st.form_submit_button("Save human evaluation")
            if save:
                if not watched or not facts.strip():
                    st.error("Watch the source and enter expected facts before saving.")
                else:
                    folder = DATA / "evaluations" / owner
                    folder.mkdir(parents=True, exist_ok=True)
                    data = {
                        "job": id,
                        "reviewer": owner,
                        "independently_reviewed": True,
                        "expected_facts": facts.splitlines(),
                        "supported_percent": accuracy,
                        "missed_events": missed,
                        "spoiler_leaks": leaks,
                        "max_timestamp_error_s": timestamp_error,
                        "query": by_id[id]["payload"],
                    }
                    (folder / (id + ".json")).write_text(json.dumps(data, indent=2))
                    st.success("Human evaluation saved locally.")
                    st.download_button(
                        "Download evaluation",
                        json.dumps(data, indent=2),
                        id + "-evaluation.json",
                    )
        else:
            st.caption("Complete a real-video recap to begin evaluation.")
