# Week 1–5: learning coverage and completion checklist

**Reviewed 10 September 2026 against the five project handouts supplied by Siva.** All five learning themes have a project mapping. The evidence supports the core app, RAG and agent workflows, plus an adapted LoRA experiment. It does **not** support declaring all five assignments fully complete.

This is a project self-audit, not an instructor grade or confirmation of submission. The handouts are the source for the requirements below; suggested tracks and optional tools are distinguished from requirements for this custom project. Private course PDFs are not redistributed here.

## At a glance

| Week | Learning demonstrated | Completion status |
|---|---|---|
| 1 — AI-assisted app development | Streamlit app, a real user problem, iterative UX changes and published code | Core learning demonstrated through the custom-app path; development screenshots, Google Doc and ≤5-minute recording not verified |
| 2 — RAG | Video ingestion → observations → embeddings → SQLite → retrieval → cited recap | Core chain demonstrated on one YouTube interval; retrieval/answer quality, numeric targets and a broader evaluated question set remain open |
| 3 — Agentic systems | Rules plus model decisions, tools, state, error recovery and durable review | Core workflow demonstrated; actual usefulness/time saved and submission materials remain unverified |
| 4 — Evaluation | Frozen synthetic cases, baseline comparison, local traces and human-review tooling | Partial: the real video agent needs reviewed labels, verified LangSmith case/model/tool traces and measured improvements |
| 5 — Fine-tuning | Separate LoRA training, held-out metrics, merge and inference checks | Core concepts demonstrated through a custom BERT-tiny experiment; exact Qwen3/LLaMA Factory exercise, cost/speed comparison and custom-submission recording not demonstrated |

**Status vocabulary:** Demonstrated = code plus a recorded run or relevant test. Partial = some evidence exists but a material requirement remains. Pending = no completed evidence identified. Adapted = the concept is implemented through a different method. Track-specific = belongs to an alternative example, not a universal requirement.

## Use one successful example to follow the product

Source: [S_9wb3g7jtY](https://www.youtube.com/watch?v=S_9wb3g7jtY&t=300). Start **05:00**, End and spoiler cutoff **08:00**. Ask what happened in this interval.

The [recorded integration test](https://github.com/sivalinb/racetime-copilot/blob/main/reports/youtube-interval-test.md) produced seven observations, five cited sentences, no reported coverage gaps, an LLM decision to summarize and a pending human-review checkpoint. It used a direct link without an upload. Its source commit is recorded in the exported JSON; it is a historical run, not a fresh evaluation of every later commit.

| Product event | What to point to | Course connection |
|---|---|---|
| User saves a URL and asks about a time range | Video workspace forms and Jobs / results | Week 1: turn a personal problem into an interactive app |
| Cold retrieval returns zero notes; inspection creates evidence | `trace`: retrieve → inspect → retrieve; seven entries in `selected` | Week 2: ingest, chunk, embed, persist and retrieve |
| Model chooses a legal next action | `trace`: `step: plan`, `mode: llm`, `action: summarize` | Week 3: stateful model decisions within application constraints |
| Generated recap is checked and saved for review | `narrative.sentences[].evidence_ids`, `generated_verified`, `awaiting_review` | Weeks 2–3: grounding and human review |
| A reviewer can inspect evidence and score it | Local trace plus Evaluation UI; actual human labels are still pending | Week 4: observability exists; quality evaluation is not yet complete |
| Separate intent classifier is trained and evaluated | LoRA dataset, adapter and held-out reports | Week 5: a separate artifact; this YouTube run did not invoke the trained router |

`generated_verified` means a model grounding check accepted the recap. It does not mean independently verified facts. `awaiting_review` does not mean approved. A processed coverage window does not establish that every event was captured.

## Week 1 — AI-assisted development

Source: **Week 1 Project Handout.pdf**, pp. 1–4. The handout explicitly permits a custom app and framework (Path B).

- **W1.1 — Define the problem and build a working app: Demonstrated.**
  - **How:** an ultrarunner who misses long broadcasts can save a video, select the missed interval and review a recap.
  - **Proof / demonstration:** [founder story](https://github.com/sivalinb/racetime-copilot/blob/main/docs/founder-story.md), [video UI](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/ui.py), and the saved 05:00–08:00 test. Walk through Videos → Ask / inspect → Jobs / results.
- **W1.2 — Collaborate with a coding assistant and iterate: Demonstrated in the development history; submission record partial.**
  - **How:** requests to use Streamlit, make instructions visible, add prompt examples and improve Python readability led to concrete changes.
  - **Proof / remaining:** repository history and [coding standard](https://github.com/sivalinb/racetime-copilot/blob/main/CONTRIBUTING.md). Capture actual development prompts and before/after screenshots in the submission document; do not substitute the 100 end-user questions for coding prompts.
- **W1.3 — Interactive data handling and visualization: Adapted.**
  - **How:** video-derived observations, time filters, source playback, evidence displays and evaluation views replace the sample CSV portfolio dashboard.
  - **Scope:** CSV charts are part of the sample workflow; Path B allows this different application. The architecture illustrations explain the design but are not measured analytics charts.
- **W1.4 — Publish the code and explain how to run it: Demonstrated.**
  - **Proof:** public repository, [README](https://github.com/sivalinb/racetime-copilot/blob/main/README.md), [setup](https://github.com/sivalinb/racetime-copilot/blob/main/docs/setup.md), tests and CI.
- **W1.5 — Google Doc, development screenshots and ≤5-minute demo: Pending verification.**
  - **Remaining:** a Google Doc covering overview, data, actual coding prompts, iterations and lessons; screenshots of the process; a recording of the working app. No matching Google Doc link or finished demo recording has been supplied for this audit.

## Week 2 — Retrieval-augmented generation

Source: **Week 2 Project Handout (Aug 2026).pdf**, pp. 1–4 (framework and tracks), pp. 5–7 (example-specific evaluations and submission).

- **W2.1 — Explicit use case, corpus and surface: Demonstrated; success targets pending.**
  - **How:** race viewers ask interval questions over timestamped observations from a selected public video in Streamlit. The demonstrated corpus is one 180-second interval containing seven model-generated notes; the publisher's recording remains the underlying source.
  - **Remaining:** specify numeric faithfulness/relevance and latency goals, then measure them. A citation check is not a measured percentage of source truth.
- **W2.2 — Ingestion, cleaning and freshness: Demonstrated for recorded input; freshness guarantee partial.**
  - **How:** [Service.inspect](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/service.py) sends bounded windows; [provider schemas](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/provider.py) validate observation structure and time bounds. Reinspection replaces evidence in the selected window.
  - **Remaining:** no measured freshness SLA or automatic detection of edited/replaced YouTube content. Live processing uses captured coverage and still awaits an active-stream test.
- **W2.3 — Chunking and embeddings: Demonstrated.**
  - **How:** inspection windows are at most 300 seconds, sampled at 1 fps; individual semantic observations become retrievable text units. Gemini Embedding 2 provides 768-dimensional document/query vectors.
  - **Proof:** the three-minute test returned seven notes; provider generation and document/query embedding integration also passed. Sampling and note extraction can miss details.
- **W2.4 — Store and retrieve: Demonstrated.**
  - **How:** [SQLite evidence storage](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/store.py) persists notes and vectors. [Agent.retrieve](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/agent.py) filters by time/availability, ranks vector similarity, takes up to 30 notes and retains related annotated conflicts.
  - **Scope:** this is dense retrieval with metadata filters, not a deployed hybrid sparse/dense retriever or separate reranker. Those are recommendations or requirements of particular sample tracks, not all custom RAG projects.
- **W2.5 — Cited generation and insufficient-evidence handling: Demonstrated, with quality limits.**
  - **How:** five sentences in the recorded recap reference valid observation IDs. A separate model grounding check runs; failed synthesis can yield labeled extracts, and missing usable evidence can produce clarification.
  - **Proof:** recorded narrative/trace plus timestamp, unknown-citation, empty-source and failure tests in [product_test.py](https://github.com/sivalinb/racetime-copilot/blob/main/tests/product_test.py). General hallucination resistance is not established.
- **W2.6 — Evaluate retrieval and answers: Partial.**
  - **How:** 40 frozen synthetic cases evaluate evidence selection. One YouTube request demonstrates integration. The [100-question library](https://github.com/sivalinb/racetime-copilot/blob/main/docs/youtube-question-library.md) supplies possible test inputs.
  - **Remaining:** execute and independently review a representative real-video question set, report retrieval/answer scores and explain failures. All 100 catalog entries are untested, with no factual golden answers. A 15-question report is specified for the policy-Q&A example; for this custom project it is a useful initial milestone, not a universal handout minimum.
- **W2.7 — Explain design choices and submit artifacts: Partial.**
  - **Proof:** code, architecture, setup and this map explain the corpus, chunking, embedding, storage and failure path.
  - **Remaining:** numeric success/latency targets, evaluation findings, Google Doc and ≤5-minute demo. Two chunking strategies, GraphRAG with 20+ nodes, support-resolution metrics, n8n and Lyzr belong to alternative tracks; they are not all required for RaceTime.

## Week 3 — Agent decisions, tools, state and review

Source: **Week 3 Project Handout (Aug 2026).pdf**, pp. 1–2 and 6–9. A custom use case and an appropriate single-agent pattern are permitted; every example agent/tool is not mandatory.

- **W3.1 — Perform a multi-step task with a clear user outcome: Demonstrated; outcome measurement pending.**
  - **How:** the agent replaces manual searching through a chosen interval with a cited recap and review workflow.
  - **Proof:** the real YouTube trace completes retrieval, inspection, retrieval, model planning and summary. Actual user time saved, completion rate and a numeric success target remain unmeasured.
- **W3.2 — Choose actions and use tools: Demonstrated.**
  - **How:** retrieve, inspect, summarize and clarify are distinct operations; the model chooses when more than one action is legal. Rules force the first retrieval and cold-source inspection.
  - **Proof:** the saved run has rule decisions followed by `mode: llm` choosing `summarize`. This is one constrained agent, not independent agents masquerading as graph nodes.
- **W3.3 — Maintain state and memory: Demonstrated.**
  - **How:** graph state contains the question, interval, selected evidence, decisions, limitations and narrative; SQLite stores jobs/evidence and LangGraph checkpoints.
  - **Proof:** [Agent](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/agent.py), [Store](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/store.py), account-persistence, lease-recovery and durable-review tests. This is job/evidence persistence, not a general conversational memory feature.
- **W3.4 — Define autonomy and side effects: Demonstrated in the design.**
  - **How:** an explicitly queued request authorizes bounded model calls and internal job/evidence writes. A recap is stored as a draft before human approval. The app does not send messages, buy services or publish the recap on the user's behalf.
  - **Limit:** internal writes are not all approval-gated. The deliberate human boundary is accepting/rejecting the recap; inspect/summarize may incur metered provider usage before that decision.
- **W3.5 — Handle failures and constrain work: Demonstrated for tested contracts.**
  - **How:** timeout and one eligible transient retry, graph iteration cap, per-job/account call budgets, cancellation, planner fallback, extractive fallback and explicit source errors.
  - **Proof:** product tests and the earlier recorded provider failures. The successful YouTube run itself did not demonstrate a retry or outage recovery.
- **W3.6 — Durable human-in-the-loop: Demonstrated across complementary evidence.**
  - **How:** `interrupt()` stores a waiting checkpoint; `Command(resume=...)` records approved/rejected and completes the graph.
  - **Proof:** the YouTube run reached `awaiting_review`; restart/resume is demonstrated by tests and the [separate synthetic-video integration](https://github.com/sivalinb/racetime-copilot/blob/main/reports/provider-integration.json). The YouTube result has not itself been human-approved.
- **W3.7 — Documentation, code and ≤5-minute demonstration: Partial.**
  - **Proof:** public implementation and illustrated architecture are present.
  - **Remaining:** documented success targets, Google Doc with coding iterations and actual working-demo recording. Instructor submission/acceptance is not verified. Multi-agent orchestration, voice and particular SaaS APIs are optional/track-specific here.

## Week 4 — Measure and improve the agent

Source: **Week 4 Project Handout (Aug 2026).pdf**, pp. 1–9. This audit follows the own-agent evaluation path. The handout's general framework calls for 30–50 labeled cases; p. 5 also mentions 50–100 as a sweet spot. Use an explicit, versioned scope rather than counting unreviewed prompts.

- **W4.1 — Define outcome metrics and numeric pass bars: Partial.**
  - **Present:** exact evidence-ID matches, routing accuracy/F1, synthetic latency and a video human-evaluation form.
  - **Remaining:** a video-agent evaluation specification with 3–5 quality/behavior/latency/cost metrics and explicit numeric thresholds. No real-video faithfulness, latency or cost pass bar has been demonstrated.
- **W4.2 — Build a representative golden dataset: Partial.**
  - **Present:** [40 frozen synthetic evidence cases](https://github.com/sivalinb/racetime-copilot/blob/main/evals-observability/datasets/evidence-golden-v1.json), checksums and versioning. These test the separate evidence workflow.
  - **Remaining:** reviewed source facts or expected behavior for 30–50 video-agent cases spanning happy paths, edges, known failures and adversarial inputs. Prefer a 40-case pilot with 20/12/6/2 cases across those groups. This is a proposed dataset, not an executed benchmark. Model-generated notes and the 100 authored questions are not reviewed labels.
- **W4.3 — Instrument case, model and tool traces: Partial.**
  - **Present:** local agent steps, job IDs, coverage, limitations, usage records and LangSmith configuration.
  - **Remaining:** verify actual LangSmith ingestion and one parent trace per evaluation case with model/tool child runs, versions, expected/predicted output, correctness, latency, errors and token metadata. Direct Gemini SDK calls do not yet demonstrate those child spans. The last external check hit quota HTTP 429; the successful YouTube run disabled external tracing.
- **W4.4 — Execute a baseline with linked per-case results: Partial.**
  - **Present:** [40/40 versus 20/40](https://github.com/sivalinb/racetime-copilot/blob/main/evals-observability/benchmarks/evidence-latest.json) on fixed synthetic evidence IDs, plus local retry/cache traces.
  - **Remaining:** a baseline evaluation of the actual video agent on the reviewed video dataset, with per-case scores and trace links. The successful URL request alone is not that baseline.
- **W4.5 — Judge quality and calibrate subjective scoring: Partial.**
  - **Present:** code validation, a model grounding check and human annotation UI.
  - **Remaining:** human source review and reliability checks for subjective scores. If an LLM judge is used for evaluation, compare it against human labels; the current grounding check is not a calibrated independent judge.
- **W4.6 — Cluster failures and quantify impact: Pending for the video evaluation.**
  - **Present:** source/provider errors and limitations are documented.
  - **Remaining:** ranked failure clusters from evaluated cases, representative trace IDs, frequency and operational impact. Do not infer dominant failure rates from a handful of integration attempts.
- **W4.7 — Make 3–4 targeted improvements and measure deltas: Pending for the video agent.**
  - **Present:** the evidence baseline shows the benefit of combined filtering rules.
  - **Remaining:** preserve a video-agent baseline, choose improvements from measured failure clusters, rerun the same dataset and report gains and regressions. A formatting cleanup or one newly working source is not an evaluated quality improvement.
- **W4.8 — Submit report, dataset, trace evidence and recording: Partial.**
  - **Present:** the [evals and observability folder](https://github.com/sivalinb/racetime-copilot/tree/main/evals-observability) explains existing evidence and limits.
  - **Remaining:** completed video evaluation report, versioned reviewed dataset, verified LangSmith trace links/screenshots and Loom walkthrough. Future monitoring thresholds can be proposed; no deployed alerting service is claimed. The handout says Week 4 is optional for the certificate, but full learning coverage still needs this work.

## Week 5 — Specialize a model with LoRA

Source: **Week 5 Project Handout (Aug 2026).pdf**, pp. 1–4. The example uses Qwen3-1.7B, support tickets, a stratified 80/20 split, ShareGPT format, LLaMA Factory/Board and a T4. The handout also allows custom exploration with GitHub assets and a Loom video.

- **W5.1 — Choose a focused labeled task and separate held-out data: Adapted and demonstrated.**
  - **How:** four race-question intents—recap, runner, verify and compare—with 144 authored training examples and 40 separately worded held-out examples.
  - **Proof:** [frozen router data](https://github.com/sivalinb/racetime-copilot/blob/main/evals-observability/datasets/router-v1.json). This is not the handout's exact support-ticket CSV or stratified 80/20 procedure; no real-user label quality is claimed.
- **W5.2 — Train a LoRA adapter with understandable choices: Adapted and demonstrated.**
  - **How:** [train_router.py](https://github.com/sivalinb/racetime-copilot/blob/main/training/train_router.py) uses PyTorch/Transformers/PEFT, BERT-tiny, rank-8 query/value adapters and a trained classifier head. Base encoder weights stay frozen; the report records 96 steps and 8,708 trainable parameters for the LoRA arm.
  - **Scope:** model, environment and training UI differ from the provided Qwen3/LLaMA Factory exercise.
- **W5.3 — Inspect training behavior: Partial.**
  - **Present:** initial/final loss and training-step counts are recorded.
  - **Remaining:** a saved per-step loss curve and training-run screenshot are not included in the current report. End-point loss values alone do not show that training stabilized throughout.
- **W5.4 — Merge and smoke-test inference: Demonstrated.**
  - **Proof:** [router-smoke.json](https://github.com/sivalinb/racetime-copilot/blob/main/reports/router-smoke.json) records four sample predictions and merge error `9.54e-7`, within `1e-5`. The handout's exact example asks for five obvious tickets; this custom lab currently has four intent examples.
- **W5.5 — Compare baseline and adapted model: Demonstrated for classification; business benefit pending.**
  - **Proof:** held-out accuracy **52.5% → 70%**, macro F1 **0.522 → 0.709**, class metrics, confusion matrices and predictions in the [recorded report](https://github.com/sivalinb/racetime-copilot/blob/main/evals-observability/benchmarks/router-recorded.json).
  - **Scope:** both arms train a classifier head; only one trains adapters. This differs from the handout's untrained generative baseline. The adapter remains outside the live video graph; reduced app latency, cost or improved video answers have not been established.
- **W5.6 — Package and explain the custom result: Partial.**
  - **Present:** training/inference code, reproducibility instructions, data, adapter and reports are in GitHub.
  - **Remaining:** a custom-project Loom and an explanation of the substitutions and errors. The exact notebook exercise remains separate. Week 5 is optional for the certificate; only the instructor can determine acceptance of the custom submission.

## Practical completion order

1. **Package the demonstrated work:** collect actual coding prompts/screenshots and record a ≤5-minute app walkthrough that shows the URL, 05:00–08:00 result, citations, trace and pending review. Add the Google Doc and recording links when available.
2. **Turn prompts into evaluations:** select varied questions, watch their source intervals and write expected facts independently. Start with a small pilot, then freeze the planned 40-case video dataset. The 100-question catalog is the starting pool, not the scorecard.
3. **Complete Week 4:** define pass bars, restore and verify LangSmith traces including model/tool child spans, run a baseline, cluster failures and measure 3–4 targeted improvements on the same dataset.
4. **Finish the Week 5 explanation:** include the training curve, a fifth clear smoke example if matching that check, and the custom-lab recording. Treat live-router deployment and cost/speed benefits as additional work until measured.

Live-stream validation and large-upload reliability remain product gaps. They should be disclosed in the capstone, but they do not require abandoning the demonstrated recorded-video scope.

## A defensible capstone statement

> RaceTime demonstrates AI-assisted app development, a working video RAG chain, a stateful agent with durable human review, reproducible synthetic evaluation and an adapted LoRA classifier. One direct YouTube interval worked end to end up to review. Full video-quality evaluation and submission evidence remain to be completed.
