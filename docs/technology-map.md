# Technology and Week 1–5 map

For a plain-language explanation of each week, read [How RaceTime applies Week 1–5](capstone-learning.md), also available in the app.

**Completion check:** [the handout audit](course-completion-audit.md) maps each core learning and submission requirement to evidence and remaining work. All five themes have coverage; Week 4 validation and several submission artifacts remain incomplete.

Each tool has a product job. The capstone applies the course themes; it does not claim every handout's exact tool sequence.

| Technology | Product use and reason |
|---|---|
| Streamlit | Simple local account, video, question, review and evaluation screens. |
| Gemini + Pydantic | Convert video into bounded observations; validate timestamps and citations; generate and check a readable recap. |
| Gemini Embedding 2 | Learned vectors retrieve evidence relevant to the user's question. |
| Python LangGraph | Bounded model decisions and actual durable human interrupt/resume. |
| SQLite | Persistent accounts, leased jobs, observations, vectors, checkpoints and usage budgets. |
| FFmpeg + yt-dlp | Validate uploaded media and capture ordinary public live streams into bounded segments. |
| Braintrust / LangSmith | Selectable hosted job/model/tool traces. Braintrust is demonstrated; local traces persist independently. |
| Nebius Token Factory | Optional Qwen judge of an answer against supplied facts; reports disagreements and remains uncalibrated. |
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
| 2: retrieval | Direct YouTube 05:00–08:00: seven observations, embeddings, retrieval and five cited sentences | Numeric targets, independent factual/timestamp labels and varied-source reliability |
| 3: orchestration | Real model-selected summarization, pending review checkpoint; restart/error tests | Planner usefulness and user completion/time targets across reviewed cases |
| 4: evaluation | 40 frozen synthetic cases, baseline comparison, verified Braintrust spans, Nebius 4/5 fixture agreement and real-review UI | Independent video golden cases, judge calibration and measured improvements; exact handout asks for LangSmith; 100 prompts remain untested |
| 5: specialization | Custom BERT-tiny LoRA, 52.5% → 70%, 96-step curves, five smoke examples and recorded local inference | Attach/share the prepared recording; confirm custom submission format. Business benefit and exact Qwen3 exercise remain separate |

The original evidence evaluation is **40/40**, versus **20/40** for naive overlap. The separate LoRA lab reached **70%**, versus **52.5%** for a frozen encoder with a trained head, on 144 training and 40 held-out authored examples. These synthetic results do not establish real-video quality. The trained classifier runs in the separate local lab; it does not control the video agent.

Siva's race experience motivates the problem. Time boundaries, traces, bounded memory and explicit failure connect it to his observability and systems background. Read [verification](../reports/verification.md) and [current status](product-status.md) before presenting validation claims.
