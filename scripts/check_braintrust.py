"""Verify server-side Braintrust ingestion; optionally make one real Nebius call."""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from uuid import uuid4

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from racetime.config import DATA, ROOT
from racetime.judge import JudgeCase, judge
from racetime.observability import braintrust_logger, record, span, trace_reference


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-nebius", action="store_true")
    args = parser.parse_args()
    logging.getLogger("braintrust").setLevel(logging.CRITICAL)
    if not os.getenv("BRAINTRUST_API_KEY"):
        raise SystemExit(
            "BRAINTRUST_API_KEY is missing; hosted verification is pending."
        )
    os.environ["RACETIME_OBSERVABILITY"] = "braintrust"
    os.environ["LANGSMITH_TRACING"] = "false"
    marker = uuid4().hex
    with span(
        "RaceTime observability check",
        inputs={"scope": "authored_fixture"},
        metadata={"verification_id": marker},
    ) as root:
        if root is None:
            raise SystemExit(
                "Braintrust initialization failed; no successful delivery is claimed."
            )
        with span(
            "Retrieve fixture references",
            "retriever",
            {"fixture": "correct-abstention"},
        ) as retrieval:
            record(
                retrieval,
                {
                    "expected_facts": [],
                    "reason": "Fixture briefing contains no result.",
                },
            )
        if args.with_nebius:
            data = json.loads(
                (
                    ROOT / "evals-observability/datasets/nebius-judge-smoke-v1.json"
                ).read_text()
            )
            verdict = judge(JudgeCase.model_validate(data["cases"][0]["input"]))
            record(root, {"judge_accept": verdict["judge_accept"]})
        else:
            record(root, {"fixture_check": True, "no_model_call": True})
        reference = trace_reference(root)
    logger = braintrust_logger()
    logger.flush()
    found = []
    for attempt in range(4):
        response = requests.get(
            f"https://api.braintrust.dev/v1/project_logs/{logger.id}/fetch",
            headers={"Authorization": "Bearer " + os.environ["BRAINTRUST_API_KEY"]},
            params={"limit": 100},
            timeout=30,
            allow_redirects=False,
        )
        if response.status_code != 200:
            raise ValueError("Braintrust trace readback failed.")
        events = response.json().get("events", [])
        root_event = next(
            (e for e in events if e.get("id") == reference["run_id"]), None
        )
        if root_event:
            found = [
                e
                for e in events
                if e.get("root_span_id") == root_event.get("root_span_id")
            ]
            names = {e.get("span_attributes", {}).get("name") for e in found}
            if "Retrieve fixture references" in names and (
                not args.with_nebius or "Nebius evaluation judge" in names
            ):
                break
        if attempt < 3:
            time.sleep(2)
    else:
        raise ValueError(
            "Expected parent and child spans not found in hosted readback."
        )
    report = {
        "status": "verified",
        "scope": "authored_fixture; not a real-video quality benchmark",
        "real_nebius_call": args.with_nebius,
        "reference": reference,
        "spans": [
            {
                key: event.get(key)
                for key in (
                    "id",
                    "span_id",
                    "root_span_id",
                    "span_parents",
                    "span_attributes",
                    "metrics",
                )
            }
            for event in found
        ],
    }
    output = DATA / "braintrust-check.json"
    output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, requests.RequestException):
        raise SystemExit(
            "Braintrust verification failed; no credential or raw provider error is printed."
        ) from None
