"""Send a labeled synthetic graph trace; verify hosted spans without Gemini calls.

Run from the repo root: python -m scripts.check_langsmith
Uses ignored .env credentials. Consumes three LangSmith traces, no Gemini quota.
"""

import json
import logging
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import langsmith as ls

from racetime.config import ROOT  # Loads the ignored environment before tracing.
from racetime.provider import Gemini
from racetime.service import Service
from racetime.store import Store


class FixtureModels:
    def generate_content(self, **kwargs):
        schema = kwargs["config"].response_json_schema["title"]
        if schema == "Observations":
            answer = {
                "events": [
                    {
                        "start": 5,
                        "end": 10,
                        "text": "Synthetic runner reaches a checkpoint.",
                        "kind": "visual",
                    }
                ],
                "limitations": ["Synthetic tracing fixture; no video was analyzed."],
            }
        elif schema == "Decision":
            answer = {
                "action": "summarize",
                "reason": "Synthetic fixture has evidence.",
            }
        elif schema == "Narrative":
            evidence = json.loads(kwargs["contents"][-1])["evidence"]
            answer = {
                "sentences": [
                    {"text": evidence[0]["text"], "evidence_ids": [evidence[0]["id"]]}
                ]
            }
        else:
            answer = {"supported": True, "explanation": "Synthetic fixture check."}
        return SimpleNamespace(
            text=json.dumps(answer),
            usage_metadata=SimpleNamespace(
                prompt_token_count=10, candidates_token_count=5, thoughts_token_count=0
            ),
        )

    def embed_content(self, **kwargs):
        return SimpleNamespace(
            embeddings=[
                SimpleNamespace(values=[1.0] + [0.0] * 767) for _ in kwargs["contents"]
            ]
        )


def main():
    logging.getLogger("langsmith").setLevel(logging.CRITICAL)
    client = ls.Client(timeout_ms=10000)
    project = client.create_project("racetime-copilot", upsert=True)
    # A synchronous write exposes quota errors before asynchronous graph tracing.
    probe = ls.Client(auto_batch_tracing=False, timeout_ms=10000)
    probe.create_run(
        id=uuid.uuid4(),
        name="RaceTime connectivity check (synthetic)",
        run_type="chain",
        project_name="racetime-copilot",
        inputs={"purpose": "Check trace ingestion; no video analyzed"},
        outputs={"synthetic": True},
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
    )
    with tempfile.TemporaryDirectory() as folder:
        store = Store(Path(folder) / "db.sqlite")
        owner = "synthetic-observability-check"
        service = Service(
            store,
            lambda *args: Gemini(*args, client=SimpleNamespace(models=FixtureModels())),
        )
        media = service.add_video(
            owner,
            "SYNTHETIC tracing fixture",
            "https://www.youtube.com/watch?v=S_9wb3g7jtY",
        )
        job_id = service.enqueue(
            owner,
            "recap",
            {
                "media": media["id"],
                "start": 0,
                "end": 30,
                "as_of": 30,
                "question": "Synthetic tracing check: what happened?",
            },
        )
        with (
            patch("racetime.agent.DATA", Path(folder)),
            ls.tracing_context(
                client=client,
                enabled=True,
                tags=["synthetic-observability-check"],
                metadata={
                    "validation": "Synthetic SDK responses; no video analyzed; token counts are fixtures"
                },
            ),
        ):
            service.process_one()
            job = store.job(owner, job_id)
            if job["status"] != "awaiting_review":
                raise RuntimeError("Synthetic workflow did not reach review")
            root_id = job["result"]["observability"]["run_id"]
            service.review(owner, job_id, "rejected")
        client.flush(timeout=15)
        runs = []
        for _ in range(5):
            runs = list(
                client.list_runs(
                    project_id=project.id, trace_id=uuid.UUID(root_id), limit=100
                )
            )
            if any(r.run_type == "llm" and r.end_time for r in runs):
                break
            time.sleep(2)
        llms = [r for r in runs if r.run_type == "llm"]
        types = {r.run_type for r in runs}
        required = {"chain", "llm", "tool", "retriever", "embedding"}
        if not required <= types or not all(r.parent_run_id for r in llms):
            raise RuntimeError(
                "Hosted child-span verification failed; check quota and workspace"
            )
        if not all(r.total_tokens == 15 for r in llms):
            raise RuntimeError("Hosted token metadata verification failed")
        root = next(r for r in runs if str(r.id) == root_id)
        review_id = store.job(owner, job_id)["result"]["observability"]["run_id"]
        review = client.read_run(review_id)
        report = {
            "verified_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "kind": "synthetic_observability_integration",
            "project": "racetime-copilot",
            "trace_url": client.get_run_url(run=root, project_id=project.id),
            "trace_id": root_id,
            "job_id": job_id,
            "span_count": len(runs),
            "run_types": sorted(types),
            "llm_spans": len(llms),
            "tokens_are_synthetic": True,
            "human_review_resume_verified": review.outputs["status"] == "completed",
            "limitation": "Verifies hosted instrumentation using synthetic SDK responses, not Gemini or video accuracy.",
        }
        target = ROOT / ".runtime" / "langsmith-check.json"
        target.write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("LangSmith verification failed:", type(exc).__name__)
        if isinstance(exc, RuntimeError):
            print(str(exc))
        detail = str(exc).lower()
        report = {
            "verified_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "blocked"
            if "429" in detail and "monthly" in detail
            else "not_verified",
            "reason": "Monthly trace limit reached"
            if "429" in detail and "monthly" in detail
            else "Hosted trace check did not pass; inspect account access and quota",
            "exception_type": type(exc).__name__,
        }
        (ROOT / ".runtime" / "langsmith-check.json").write_text(
            json.dumps(report, indent=2)
        )
        raise SystemExit(1) from None
