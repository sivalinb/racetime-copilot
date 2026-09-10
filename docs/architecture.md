# Architecture

## Illustrated overview

![How a race question runs](../public/architecture/racetime-illustrated-architecture.png)

[Open full-size illustration](../public/architecture/racetime-illustrated-architecture.png). Read left to right: input and queue → constrained agent → evidence and checks → human review. The laptop, decision trail, evidence store and review desk illustrate the local product. Sample race events are illustrative, not measured results. The separate lab and observability band shows supporting capstone work.

This is the first tab in Streamlit's **Technical architecture** panel. The original engineering plates remain in the next two tabs. The hand-drawn presentation is inspired by [CryoWatch's illustrated workflow](https://github.com/archanajalamadugu/CryoWatch). RaceTime artwork was created with the built-in image-generation tool; [generation prompt](architecture-image-prompt.md).

## Engineering plates

These diagrams describe the implementation and validation status on **10 September 2026**. Blue marks application rules, amber model operations, green human review and results, and red blocked or unverified paths. Dashed connectors indicate conditional paths; labelled dashed boxes group components.

### I. System architecture

![System architecture](../public/architecture/racetime-system-architecture.svg)

[Open full-size SVG](../public/architecture/racetime-system-architecture.svg). Follow the video request from Streamlit into the SQLite job queue, worker and LangGraph tools. The lower band separates the TypeScript evidence demo, evaluation and LoRA experiment, and deployment preparation from the local video product.

### II. Question lifecycle

![Question lifecycle](../public/architecture/racetime-decision-flow.svg)

[Open full-size SVG](../public/architecture/racetime-decision-flow.svg). Follow retrieval into the permitted-action planner, then inspect, summarize or clarify. Generated answers pass citation checks and grounding before a durable human-review pause. A completed job records a decision; it does not certify truth.

Both plates are available before sign-in in Streamlit's collapsed **Technical architecture** panel, with SVG downloads. The box-and-arrow engineering presentation is inspired by [CryoWatch](https://github.com/archanajalamadugu/CryoWatch); the diagrams and implementation details are original to RaceTime.

To update the editable diagrams, change `scripts/build_architecture.py` and run:

```bash
python scripts/build_architecture.py
```

## Local processes

`python scripts/run_product.py` starts the video workspace and worker on localhost:8501. It needs Python and a Gemini key. `run_demo.py` also includes the original TypeScript evidence API on port 3000 and the key-free fictional demo. The optional React screen uses that API.

## Video workflow

A job first retrieves observations. A cold recorded source is inspected within the requested interval. Gemini then chooses from the permitted inspect, summarize or clarify actions; the graph limits iterations and records fallbacks. Learned 768-dimensional embeddings rank observations. A separate Gemini call checks generated sentences against their cited observations. Rejected generation falls back to clearly labelled extracts.

The agent pauses at a real LangGraph interrupt. SQLite checkpoints allow an account owner to approve or reject after a process restart. Approval records the user's decision; it does not prove factual accuracy.

## Time and coverage

A complete observation must fit inside the requested interval and have become available by the spoiler cutoff. Gemini receives bounded video intervals, sampled at one frame per second. Sampling can miss brief events, and provider timestamp or factual errors still require review. Processed windows, missing coverage and provider limitations are shown with results.

Live capture uses public YouTube access through yt-dlp and FFmpeg. It captures consecutive 60-second segments while processing completed ones. Sessions are limited to 15 minutes. The user supplies the current elapsed broadcast time; network delay affects alignment. Interrupted live jobs require a fresh time origin. Uncaptured past footage is unavailable.

## Persistence and limits

Local accounts use salted PBKDF2 password hashes and owner-scoped queries. Jobs, observations, usage and checkpoints persist under ignored `.runtime/`. Recorded jobs have leases and bounded restart recovery; cancellation is checked between calls. Provider calls have a 120-second timeout and one retry for transient service errors. Defaults are three active jobs per account, 32 generation/embedding calls per job, 120 calls per account per day and 500 MB retained uploads per account. A single upload is limited to 100 MB. Small MP4s use inline input; larger files use Google's Files API.

SQLite is intended for this single-host local product. The prepared public container requires OIDC with verified, allow-listed emails. Container build, hosted sign-in and public operation still need validation.

## Evidence demo and specialization

The original TypeScript workflow uses Zod contracts, VTT/SRT/JSON imports, lexical ranking and deterministic hashed vectors. Its D1 store and byte-weighted LRU remain separate from the video workspace. The cache holds 500 KB of serialized results for five minutes and includes source revision in its key. Manual live append invalidates old revisions. Its review records are ordinary saved decisions, unlike the video workspace's graph checkpoint.

The BERT-tiny LoRA lab is a separate experiment, not the production planner. Local traces work without LangSmith; external traces need an account with available quota. See [status](product-status.md) for measured validation and blockers.
