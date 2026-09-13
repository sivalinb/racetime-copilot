"""Aggregate source-reviewed annotations, including unanswerable questions."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from racetime.config import DATA
from racetime.evaluation import summarize_annotations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DATA / "evaluations")
    parser.add_argument("--output", type=Path, default=DATA / "real-evaluation.json")
    args = parser.parse_args()
    records = [json.loads(f.read_text()) for f in sorted(args.input.rglob("*.json"))]
    result = summarize_annotations(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    if not result["count"] or result["excluded"]:
        raise SystemExit(
            "Evaluation incomplete: missing or invalid annotations; see report."
        )


if __name__ == "__main__":
    main()
