# Learning guide

RaceTime answers one question: **what happened during the part of the race I missed?**

Start the demo from the README, try the first 15 minutes, then read these files in order.

## The main files

| File | What it does |
|---|---|
| `app.py` | The Streamlit screen: choose a source, ask, import, review and inspect history. |
| `demo/client.py` | Calls the local backend and keeps one session for each Streamlit user. |
| `lib/contracts.ts` | Defines a source, observation, question and result. Rejects invalid times and data. |
| `lib/importers.ts` | Turns VTT, SRT and JSON into timestamped observations. |
| `lib/retrieval.ts` | Finds observations inside the requested interval and ranks relevant ones. |
| `lib/workflow.ts` | Connects the LangGraph steps: intent, retrieval, one retry, checking and recap. |
| `lib/cache.ts` | Reuses a result only when the source revision and question still match. |
| `lib/store.ts` | Saves sources, observations, runs and review decisions in local D1. |
| `data/demo.ts` | The fictional Canyon Relay race used by the demo. |

`app/api/` exposes the four backend endpoints. `scripts/run_demo.py` starts the local services. `tests/` checks behavior; `reports/` records measured results. `training/` contains the separate LoRA experiment. The optional React screen is `app/page.tsx`.

## Follow one request

1. Streamlit sends the source, start, end, cutoff and question to `/api/recap`.
2. The backend validates them and looks for a matching cached result.
3. If needed, LangGraph retrieves eligible observations and retries one simulated transient failure.
4. It checks annotated claims for disagreement and excludes obvious instruction-like text.
5. The result contains source observations, warnings and a trace. The user can save a review decision.

## Four useful concepts

**Observation:** a piece of evidence with start/end times, text and a kind such as commentary or timing. Its time of availability matters too.

**LangGraph:** named workflow steps connected by edges. Here the steps follow explicit rules. There is no live LLM planner yet.

**Grounding:** each finding comes from an observation. The current recap copies evidence rather than generating a new narrative.

**Weighted LRU:** a cache bounded by the size of its stored results. Older entries expire, and source revisions prevent old evidence from being reused after an update.

## What to change first

To add a demo event, edit `data/demo.ts`. To change what qualifies as evidence, read `lib/contracts.ts` and `lib/retrieval.ts` together, then run `npm test` and `npm run eval`. To change the screen, edit `app.py` and run `python tests/streamlit_smoke.py` with the backend running.

The Python UI and TypeScript backend are both required today. Keeping one tested evidence pipeline avoids different recap rules in the two interfaces. A full Python conversion would be a separate implementation change.

You can ignore `node_modules/`, `.venv/`, `.wrangler/` and build output while learning the code. Framework configuration supports the existing backend; it does not contain the race reasoning.
