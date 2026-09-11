# Product completion status

The local implementation is ready for continued testing. **It is not yet a validated race-video product.** Checked on 10 September 2026.

| Capability | Working implementation | Verification / remaining work |
|---|---|---|
| Small uploaded MP4 | Inline Gemini video extraction, learned retrieval and cited recap | Real six-second red/blue clip passed; two correctly timestamped observations, generated recap and review after restart |
| Recorded YouTube | Bounded direct URL analysis | `S_9wb3g7jtY` 05:00–08:00 passed: seven observations and cited recap awaiting review; no upload. One source/interval only; [test report](../reports/youtube-interval-test.md) |
| Large upload | Files API processing path | Earlier processing returned HTTP 500; larger-upload end-to-end success remains unverified |
| Agent decisions | Bounded Gemini retrieve/inspect/summarize/clarify graph, fallback and call budgets | Real small-video graph passed; 21 local product tests pass with provider fixtures |
| Summary grounding | Evidence IDs, separate model check, explicit extractive fallback | Integration passed; independent race factual review still needed |
| Semantic retrieval | Learned Gemini Embedding 2 vectors and strict time filters | Real generation and 768-dimensional embedding checks passed |
| Durable review | LangGraph interrupt and SQLite checkpoints | Automated and real-provider recap review resumed after restart |
| Background jobs / accounts | Persistent local login, account isolation, leases, cancellation and recovery | Local contract and Streamlit tests pass |
| Live capture | Continuous public YouTube segments, explicit coverage and last-15-minute query | Active race-stream test deferred at the user's request; clock alignment remains unmeasured |
| Real evaluation | Human annotation screen and aggregation command | No independently reviewed race dataset yet; no real-race quality score claimed |
| Tracing | Local graph traces and LangSmith configuration | Local traces work. LangSmith ingestion returned HTTP 429: monthly trace quota exhausted |
| Public hosting | Docker/Caddy/OIDC configuration and backup script | Deferred: local product first. Container build and hosted authentication are unverified |

The default generation model is `gemini-3.5-flash`. Small MP4s up to 12 MB use inline input; larger files use the provider Files API. An API key alone does not guarantee access to every model or video source. There is no automatic bypass of unavailable/restricted video.

The original evidence demo remains the dependable key-free presentation path: **17 tests and 40/40 synthetic cases**, versus 20/40 for naive overlap. The separate BERT-tiny LoRA lab reached 70% on authored held-out requests; it is not deployed as the planner.

## Finish validation

1. Analyze short race MP4s and independently review at least 10 varied intervals in Evaluation.
2. Expand the successful YouTube interval check to varied sources; recheck the earlier failed URL and Files API.
3. Test a currently live public race stream when one is available.
4. Restore LangSmith quota, restart with tracing enabled and confirm an external run.

See [setup](setup.md) for exact account and launch steps, and [verification](../reports/verification.md) for test scope.
