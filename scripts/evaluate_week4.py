"""Save calibration and paired interaction evidence without certifying a release."""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from racetime.evaluation import calibrate_judge, interaction_report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    study = json.loads(raw)
    calibration = calibrate_judge(study.get("calibration", []))
    interactions = interaction_report(study.get("interaction_runs", []))
    missing = []
    if not calibration["both_label_classes_present"]:
        missing.append(
            "Judge calibration needs human-accepted and human-rejected cases."
        )
    if not interactions["paired_complete"]:
        missing.append(
            "Interaction tests need the same case/repeat pairs in all four cells."
        )
    for field in (
        "dataset_version",
        "rubric_version",
        "code_revision",
        "model_version",
        "source_snapshot",
        "split_manifest",
        "label_review_record",
        "release_criteria",
    ):
        if not study.get(field):
            missing.append(f"Missing {field}.")
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "study": study,
        "calibration": calibration,
        "interactions": interactions,
        "missing_evidence": missing,
        "release_status": "blocked" if missing else "manual_review_required",
        "release_note": "No automatic release approval. Review label independence, split leakage, calibrated judge errors, per-case regressions and predeclared quality bars. Faster or safer alone cannot override a failed quality bar.",
    }
    output = args.output or Path(".runtime/week4") / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise SystemExit(
            "Report already exists; choose a new output to preserve prior results."
        )
    output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
