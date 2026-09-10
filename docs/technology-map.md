# Technology and Week 1–5 map

Each tool has a product job. The capstone applies the course themes; it does not claim every handout's exact tool sequence.

| Technology | Product use and reason |
|---|---|
| Streamlit | Simple local account, video, question, review and evaluation screens. |
| Gemini + Pydantic | Convert video into bounded observations; validate timestamps and citations; generate and check a readable recap. |
| Gemini Embedding 2 | Learned vectors retrieve evidence relevant to the user's question. |
| Python LangGraph | Bounded model decisions and actual durable human interrupt/resume. |
| SQLite | Persistent accounts, leased jobs, observations, vectors, checkpoints and usage budgets. |
| FFmpeg + yt-dlp | Validate uploaded media and capture ordinary public live streams into bounded segments. |
| LangSmith | Optional external graph traces; local traces remain available when its quota is exhausted. |
| TypeScript + Zod + D1 | Original key-free evidence API with validated imports and session-scoped persistence. |
| VTT/SRT/JSON + lexical/hashed ranking | Reproducible evidence-demo ingestion and retrieval without an API key. |
| Byte-weighted LRU | Bound evidence-demo memory and invalidate results when source revisions change. |
| unittest + Node tests + Streamlit AppTest | Check isolation, restart recovery, time rules, provider contracts and user workflows. |
| PyTorch + Transformers + PEFT + scikit-learn | Separate LoRA intent-router training, evaluation, merge and inference experiment. |
| Docker + Caddy + OIDC | Prepared HTTPS hosting path with persistent storage and allow-listed sign-in; local scope comes first. |
| React + shadcn + WebMCP | Optional browser interface to the original evidence API. |

| Week | Applied learning | Remaining validation |
|---|---|---|
| 1: app | Streamlit workflow, accounts, persistence and background processing | Race-fan usability feedback |
| 2: retrieval | Bounded video ingestion, learned embeddings, citations and generated summaries | Provider video reliability and independent factual/timestamp labels |
| 3: orchestration | Legal model-selected actions, retries, budgets, checkpointed human review | Real planner usefulness across reviewed cases |
| 4: evaluation | Synthetic baseline comparison, restart/isolation tests, local traces and real-review UI | Human-reviewed race cases and external LangSmith quota |
| 5: specialization | BERT-tiny LoRA, held-out comparison, merge and inference check | Exact optional Qwen3/LLaMA Factory exercise remains separate |

The original evidence evaluation is **40/40**, versus **20/40** for naive overlap. The separate LoRA lab reached **70%**, versus **52.5%** for a frozen encoder with a trained head, on 144 training and 40 held-out authored examples. These synthetic results do not establish real-video quality. The trained classifier is not deployed.

Siva's race experience motivates the problem. Time boundaries, traces, bounded memory and explicit failure connect it to his observability and systems background. Read [verification](../reports/verification.md) and [current status](product-status.md) before presenting validation claims.
