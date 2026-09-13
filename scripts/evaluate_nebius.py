"""Run a capped set of judge cases, preserving failures and optional calibration labels."""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from racetime.evaluation import calibrate_judge
from racetime.judge import JudgeCase, judge


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--max-cases", type=int, default=5)
    args = p.parse_args()
    raw = args.input.read_bytes()
    dataset = json.loads(raw)
    rows = dataset["cases"]
    if not 1 <= len(rows) <= args.max_cases <= 100:
        raise SystemExit(
            "Dataset must fit the explicit 1–100 case request cap; nothing was sent."
        )
    cases = [JudgeCase.model_validate(row["input"]) for row in rows]
    if len({case.case_id for case in cases}) != len(cases):
        raise SystemExit("Case IDs must be unique; nothing was sent.")
    if any(
        "human_accept" in row and type(row["human_accept"]) is not bool for row in rows
    ):
        raise SystemExit("Human verdicts must be explicit booleans or omitted.")
    output = args.output or Path(".runtime/nebius") / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json"
    )
    if output.exists():
        raise SystemExit(
            "Output exists; choose a new path to preserve previous results."
        )
    results, errors, labels = [], [], []
    for case, row in zip(cases, rows, strict=True):
        try:
            result = judge(case)
            results.append(result)
            if "human_accept" in row:
                labels.append(
                    {
                        "id": case.case_id,
                        "human_accept": row["human_accept"],
                        "judge_accept": result["judge_accept"],
                    }
                )
        except ValueError:
            errors.append(
                {
                    "case_id": case.case_id,
                    "error": "Judge request failed; no score assigned.",
                }
            )
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dataset_sha256": hashlib.sha256(raw).hexdigest(),
        "dataset_provenance": dataset.get("provenance", "unspecified"),
        "results": results,
        "errors": errors,
        "calibration": calibrate_judge(labels),
        "calibration_rows": labels,
        "release_status": "not_established",
        "note": "Fixture labels are smoke-test expectations, not independent human calibration. Never promote judge outputs to golden labels.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2))
    print(
        json.dumps(
            {
                "report": str(output),
                "completed": len(results),
                "failed": len(errors),
                "calibration": report["calibration"],
            },
            indent=2,
        )
    )
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
