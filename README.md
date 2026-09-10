# RaceTime Copilot

> Catch up on a missed race interval with timestamped evidence and no future spoilers.

Built by Siva Babu, an ultramarathoner and race organizer, for an agentic AI capstone.

![RaceTime Copilot](public/art/overview.png)

## The problem

You miss 15 minutes of a long race broadcast. Finding the important moments means scrubbing through video, checking runner names and reconciling conflicting commentary and timing graphics.

RaceTime lets you choose an interval, ask what happened, and inspect the source observations behind the recap.

**Today:** it works with imported captions and observations. Gemini is deferred; a YouTube link alone does not analyze a video. The included race is fictional.

## Quick start

Requires Python 3.11+ and Node.js 22.13+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm ci
python scripts/run_demo.py
```

Open **http://localhost:8501**. No API key is needed. The launcher starts Streamlit and the local backend. Stop with Ctrl+C.

## Try one scenario

Choose **Canyon Relay**, enter `00:00` to `15:00`, set the cutoff to `15:00`, and ask **What happened?**

Two ridge reports disagree. RaceTime shows both, flags the conflict, and excludes the later timing update. Inspect the trace, approve or reject the recap, and export it.

| Scenario | What to look for |
|---|---|
| Missed interval | Only observations fully inside your time range |
| Conflicting reports | Both claims shown; no invented winner |
| Missing evidence | An explicit insufficient-evidence response |
| Retrieval failure | One retry, recorded in the trace |
| Live evidence update | Appended observations create a new source revision |

## How it works

```text
Import captions/observations → choose interval → retrieve → check → recap → human review
```

Streamlit displays the result. A TypeScript LangGraph workflow retrieves and checks evidence. Local D1 stores sources and reviews; a byte-weighted LRU reuses matching requests. The workflow currently uses rules and extractive text, with no model-driven planning.

## Check it

```bash
npm test                     # 17 unit tests
npm run eval                 # 40 synthetic evidence cases
python tests/streamlit_smoke.py  # with the local demo running
```

The evidence workflow passed **40/40** synthetic cases versus **20/40** for the naive baseline. A separate LoRA routing experiment scored **70%** versus **52.5%** for its baseline. These results do not establish real-video quality; the trained router is not used in the app.

## Read next

| Document | Purpose |
|---|---|
| [Six-page brochure](docs/RaceTime-Copilot-Brochure.pdf) | Problem, audience, workflow, technology, results and next steps |
| [Learning guide](docs/learning-guide.md) | What the main files do and where to start |
| [Demo guide](docs/demo-guide.md) | Five-minute walkthrough and import examples |
| [Week 1–5 map](docs/technology-map.md) | What is implemented and what remains |
| [Architecture](docs/architecture.md) | Time rules, storage and operating limits |

Automatic livestream ingestion and Gemini analysis remain future work. This is a local prototype; a full browser refresh may start a new session. The optional React interface is at port 3000 and has a separate session.
