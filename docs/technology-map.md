# Technology and Week 1–5 map

Each technology has a job in the product. This is an adapted capstone, not a claim that every handout's exact tool sequence is finished.

## Technology → product job

| Technology | Why RaceTime uses it |
|---|---|
| Streamlit + requests | A simple local screen with a separate backend session for each user. |
| TypeScript + Zod | Shared data contracts and validation of time ranges and imports. |
| VTT / SRT / JSON | Bring captions, timing records and visual observations into one evidence format. |
| Lexical ranking + hashed vectors | Retrieve relevant observations reproducibly without a provider key. |
| LangGraph | Named workflow steps, conditional retry and an inspectable trace. |
| D1 / SQLite | Save imported evidence, recaps and human review decisions. |
| Byte-weighted LRU | Reuse stable requests within a memory budget; invalidate on source updates. |
| Node test runner + Streamlit AppTest | Check evidence rules and the complete local user flow. |
| PyTorch + Transformers + PEFT | Run the separate BERT-tiny LoRA intent-routing experiment. |
| scikit-learn | Measure classifier accuracy, F1 and confusion by intent. |
| React + shadcn + WebMCP | Optional browser interface and bounded browser-agent recap action. |
| LangSmith | Optional external tracing configuration; local traces are the verified path. |
| Gemini | Planned video-to-observation adapter; not connected. |

## Course coverage

| Week | Working implementation | Remaining work |
|---|---|---|
| 1: working app | Streamlit controls, imports, saved review and history | Real-user feedback |
| 2: retrieval | Cue ingestion, ranking, timestamps, time boundaries and insufficient-evidence responses | Learned embeddings, LLM synthesis and real-video grounding |
| 3: orchestration | LangGraph state, conditional retry, related-claim checks and human review | Model-driven planning and durable graph pause/resume |
| 4: evaluation | 40 synthetic cases, baseline comparison, local traces, latency and cache visibility | Independent labels, real-race cases and external LangSmith verification |
| 5: specialization | LoRA training, held-out comparison, adapter merge and inference check | Exact Qwen3 / LLaMA Factory workflow; current experiment uses BERT-tiny |

## Measured results

- Evidence evaluation: **40/40**, versus **20/40** for the naive overlap baseline.
- Unit tests: **17 passed**. Streamlit and API integration flows also passed.
- LoRA experiment: **70%** held-out accuracy, versus **52.5%** for the frozen encoder with a trained head; 144 training and 40 held-out authored examples. The app keeps its rule router.

All datasets above are synthetic. These scores do not measure real-video understanding. See [workflow results](../reports/workflow-evaluation.json), [router results](../reports/router-evaluation.json), [merge check](../reports/router-smoke.json) and [verification](../reports/verification.md).

The race problem comes from Siva's ultramarathon and organizing experience. Time boundaries, traces, cache behavior and explicit uncertainty connect it to his observability and systems background.
