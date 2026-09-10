# RaceTime Copilot

**Catch up on any available race-video interval, with evidence you can inspect.**

Pick a time range, ask what happened, and review timestamped observations. Follow a runner, see conflicting reports, and avoid evidence beyond your spoiler cutoff.

![RaceTime overview](public/art/overview.png)

## Try it locally

Requires Python 3.11+ and Node.js 22.13+.

```bash
npm ci
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-demo.txt
python scripts/run_demo.py
```

Open **http://localhost:8501** for the Streamlit demo. The launcher starts the shared backend on port 3000 when needed. No API key is needed; local D1 tables initialize on first use. Stop with Ctrl+C.

The optional React workbench remains at `http://localhost:3000` (`npm run dev`). Each interface has its own session and imported sources. Streamlit preserves its backend session across reruns; a full browser refresh may start a new session.

1. Keep the fictional Canyon Relay source selected.
2. Request `00:00` to `15:00` and ask **What happened?**
3. Inspect the conflicting ridge reports and their timestamps.
4. Approve or reject the recap, inspect its trace, and export JSON.
5. Import your own VTT, SRT, or JSON observations to try another source.

## What works today

- Recorded-source transcript imports and timestamp-linked YouTube playback.
- Live **evidence append** with revision checks; no automatic livestream ingestion.
- Strict interval and spoiler boundaries, runner filtering, insufficient-evidence responses.
- LangGraph retrieval, bounded failure recovery, related-claim checks, and extractive recaps.
- Persistent sources, run history and review decisions, plus a byte-weighted LRU cache.
- Browser WebMCP `summarize_interval` tool when supported.
- A separate, reproducible LoRA intent-routing experiment.

**A pasted URL alone does not analyze a video.** Gemini is deferred. Recaps currently quote imported evidence; an LLM has not watched the stream. Demo names and events are fictional.

## Check the project

```bash
npm run check
npm test
npm run eval
npm run build
# With the development server running:
npm run test:api
python tests/streamlit_smoke.py
```

The evaluation report includes **40 synthetic cases**. These are not independently reviewed real-race benchmarks. See [measured results](reports/workflow-evaluation.json) and [LoRA results](reports/router-evaluation.json).

## Explore

- [Illustrated product pitch](docs/RaceTime-Copilot-Brochure.pdf)
- [Technology and Week 1–5 map](docs/technology-map.md)
- [Architecture and limits](docs/architecture.md)
- [Demo guide and import examples](docs/demo-guide.md)
- [LoRA experiment](training/README.md)

This is a local capstone prototype. Browser-session isolation is not production account authentication. Hosting is not configured; the attempted Sites registration hit the account's hosting limit.
