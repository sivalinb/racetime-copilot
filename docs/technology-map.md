# Product use cases, technology and learning coverage

RaceTime adapts the five course themes to an endurance-race catch-up product. It does **not** claim every handout's exact tool sequence is complete. Gemini was explicitly deferred; provider credentials and independent human review remain outstanding.

| Technology | Product use case | Why it belongs | Implementation evidence |
|---|---|---|---|
| React, TypeScript, shadcn components | Choose source, time range, runner and question; review and import evidence | Makes the workflow usable and keeps data contracts explicit | `app/page.tsx`; browser recap, review and WebMCP checks |
| Zod | Reject reversed intervals, invalid observations and out-of-coverage inputs | Keeps time constraints enforceable outside model prompts | `lib/contracts.ts`; unit and API checks |
| VTT/SRT/JSON ingestion | Bring captions and structured timing/visual observations | A provider-independent way to use evidence now | `lib/importers.ts`, `/api/sources` |
| BM25-style lexical ranking | Retrieve relevant commentary and observations | Understandable baseline for names, places and exact terms | `lib/retrieval.ts` |
| Deterministic 128-dimensional hashed vectors | Tie-breaking similarity in retrieval | Reproducible with no key; **not learned semantic embeddings** | `embed()`; lexical evidence is required for topic matches |
| Time and availability filtering | Ask any available interval without future leakage | Filtering before ranking protects the requested scope | Full-cue containment plus `availableAt <= asOf` |
| LangGraph | State transitions, retrieval, bounded retry, related-claim verification | Explicit control flow and inspectable execution | `lib/workflow.ts`; injected transient failure test |
| Human review | Approve/reject a saved recap | A human can inspect uncertain evidence before sharing | D1 run record; `/api/review`; UI controls |
| Local D1 / SQLite | Persist imports, observations, history and review | Reproducible local storage with an eventual cloud binding path | Prepared statements and scoped queries in `lib/store.ts` |
| Byte-weighted LRU | Repeated catch-up requests over stable evidence | Demonstrates memory bounds, recency, TTL and revision invalidation | `lib/cache.ts`; meaningful eviction and mutation tests |
| Node test runner + tsx | Regression and evaluation workflows | Reproducible evidence beyond a happy-path demo | `tests/`, `scripts/evaluate.ts`, `reports/` |
| Local traces + LangSmith-compatible graph configuration | Explain failures and measure latency | Keeps per-case execution visible; optional external tracing later | Local reports verified; external LangSmith export **not verified** |
| PyTorch + Hugging Face Transformers | Train and evaluate a small intent classifier | A manageable local specialization experiment | `training/train_router.py` |
| PEFT LoRA | Adapt query/value projections while base encoder stays frozen | Tests specialization with far fewer trainable weights | Rank 8 adapter; 8,708 trainable parameters including classifier |
| scikit-learn | Accuracy, macro/per-class precision, recall, F1 and confusion matrix | Makes failures visible by routing intent | `reports/router-evaluation.json` |
| Adapter merge + inference | Fold learned deltas into the base model | Confirms the trained artifact can be used for inference | `training/infer.py`; `reports/router-smoke.json` |
| WebMCP | Let a browser agent request a bounded recap | Reuses the same validated product action | `summarize_interval` browser test passed |
| Gemini video understanding | Future audio/visual evidence extraction from bounded video | Needed for the user's original "watch this interval" experience | **Deferred, no provider call or video analysis claimed** |

## Week-by-week mapping

| Week | Course learning | RaceTime implementation | Remaining gap |
|---|---|---|---|
| 1 | Build and iterate on a working data app | Usable workbench, persistent backend, browser/API checks | Real-user usability feedback |
| 2 | Ingest, clean, chunk, embed, retrieve, ground and refuse | Cue chunks, ranking, timestamps, insufficiency, time/availability boundaries | Learned embeddings and LLM synthesis; real-video grounding evaluation |
| 3 | State, tools, branching, retries, human checkpoint | LangGraph state and conditional retry; corroborating-claim inspection; stored human review | Model-driven planning and durable graph pause/resume are not implemented |
| 4 | 30–50 golden cases, traces, quality, latency/cost, measured improvements | 40 synthetic cases; naive-overlap baseline 20/40 vs bounded workflow 40/40; local per-case traces; provider calls/cost 0 | Independent label review, real race cases, verified LangSmith trace links and a demo recording |
| 5 | Specialize a small model with LoRA, evaluate, merge and smoke-test | 144 training/40 held-out authored requests; frozen-encoder baseline vs rank-8 LoRA; full metrics and merge equivalence | Adapted BERT encoder experiment, **not** the handout's Qwen3-1.7B/LLaMA Factory implementation |

## Why the choices fit Siva's background

Race organizing and ultramarathon experience identify meaningful viewer questions. Observability experience informs time boundaries, visible uncertainty, traceable errors and operational metrics. The weighted LRU connects the product to the GPU benchmarking/observability interview topic: bounded memory, expiry, revision invalidation and explicit measurement. This cache is a process-local prototype, not a distributed GPU scheduling or benchmarking system.

## Sources

- User-provided Week 1–5 project handouts inform the learning themes; they are references, not instructions to submit work or contact anyone.
- [LangGraph overview](https://docs.langchain.com/oss/javascript/langgraph/overview): stateful workflow orchestration.
- [PEFT LoRA](https://huggingface.co/docs/peft/en/developer_guides/lora): low-rank adaptation and merging.
- [Gemini video understanding](https://ai.google.dev/gemini-api/docs/video-understanding): future multimodal video input; actual selected-video support remains untested.
