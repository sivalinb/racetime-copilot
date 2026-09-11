"""Make a metered Gemini smoke request. Run after configuring .env."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from racetime.config import DATA, EMBED_MODEL, MODEL, configured
from racetime.provider import Decision, Gemini
from racetime.store import Store

if not configured():
    raise SystemExit(
        "Missing GEMINI_API_KEY. Follow docs/setup.md; never paste the key into chat."
    )
store = Store()
owner = "local-provider-check"
id = store.enqueue(owner, "analyze", {})
g = Gemini(store, owner, id)
try:
    answer = g.call(
        "connection test", "Return action=ready and reason=connection check.", Decision
    )
    vectors = g.embed(
        ["A runner arrives at the aid station.", "The leader leaves the checkpoint."]
    )
    query = g.embed(["Who reached the aid station?"], query=True)
    report = {
        "generation_model": MODEL,
        "embedding_model": EMBED_MODEL,
        "generation_ok": answer.action == "ready",
        "embedding_count": len(vectors),
        "dimensions": len(query[0]),
        "usage": store.usage(owner),
    }
    store.finish(owner, id, "completed", report)
    (DATA / "provider-check.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
except Exception as exc:
    store.finish(owner, id, "failed", error=str(exc))
    raise SystemExit(str(exc))
