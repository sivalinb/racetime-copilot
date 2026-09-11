"""Run a real provider smoke test. This is integration validation, not human ground truth."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from racetime.config import DATA
from racetime.service import Service

p = argparse.ArgumentParser()
p.add_argument("--url", required=True)
p.add_argument("--start", type=float, default=600)
p.add_argument("--end", type=float, default=660)
args = p.parse_args()
svc = Service()
owner = "local-real-video-verification"
m = svc.add_video(owner, "Real race integration check", args.url)
id = svc.enqueue(
    owner,
    "recap",
    {
        "media": m["id"],
        "start": args.start,
        "end": args.end,
        "as_of": args.end,
        "question": "What happened in this interval? Describe what is visible or heard; do not invent runner identities.",
    },
)
print("Queued real video integration job " + id, flush=True)
# Use the same processor as the background worker.
while svc.store.job(owner, id)["status"] == "queued":
    if not svc.process_one():
        break
j = svc.store.job(owner, id)
report = {
    "job_id": id,
    "source_url": m["url"],
    "interval": [args.start, args.end],
    "status": j["status"],
    "error": j["error"],
    "result": j["result"],
    "validation_scope": "Real provider integration only. Factual accuracy requires independent human video review.",
}
(DATA / "real-video-check.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
if j["status"] == "failed":
    raise SystemExit(1)
