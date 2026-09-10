# Learning guide

RaceTime asks: **what happened during the part of the race I missed?**

Start with the video workspace in the README. Read these files in order:

| File | What it does |
|---|---|
| `app.py`, `racetime/ui.py` | Streamlit workspace selection, accounts, videos, jobs, review and evaluation. |
| `racetime/service.py` | Validates sources and intervals, inspects video, processes jobs and captures live segments. |
| `racetime/provider.py` | Gemini video, learned embeddings, planner, summary and grounding-check calls. |
| `racetime/agent.py` | LangGraph's permitted decisions, retrieval, cited recap and durable human interruption. |
| `racetime/store.py` | Account-scoped SQLite records, leases, usage limits and evidence coverage. |
| `racetime/worker.py` | Processes queued work outside the browser session. |
| `scripts/run_product.py` | Starts the local video product without Node. |
| `tests/product_test.py` | Checks contracts, isolation, failure handling and restart behavior with provider fixtures. |

## Follow one video question

1. Save a video and queue a question for a fixed interval.
2. The worker retrieves eligible evidence, inspecting a cold recorded source when needed.
3. The bounded planner chooses a permitted next action.
4. Gemini writes a cited recap and checks it against the observations. Failed generation is labelled and replaced with extracts.
5. LangGraph pauses. Review source timestamps, then approve or reject; the checkpoint survives a restart.

An **observation** is a timestamped report, not ground truth. **Grounding** connects a sentence to observations; a second model check can still be wrong. **Coverage** tells you which windows were processed and which are missing. Real-race quality needs independent human review.

## Original evidence demo

Use `scripts/run_demo.py` to include the fictional race scenario. `demo/client.py` calls the TypeScript API; `lib/contracts.ts` validates input, `lib/importers.ts` parses cues, `lib/retrieval.ts` ranks evidence, `lib/workflow.ts` orchestrates it, and `lib/cache.ts` implements the weighted LRU. That cache belongs to the evidence demo, not the Gemini video jobs.

`training/` contains the separate BERT-tiny LoRA experiment. Its classifier is not deployed. Ignore `.venv/`, `node_modules/`, `.runtime/` and `.wrangler/` while learning the code. Never publish their credentials or runtime data.

For setup and actual validation limits, read [setup](setup.md) and [status](product-status.md).
