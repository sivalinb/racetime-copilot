# Product completion status

The local implementation is ready for continued testing. **It is not yet a validated race-video product.** Reviewed against the implementation and recorded demo on 12 September 2026. [Submission review](../reports/submission-review.md).

| Capability | Working implementation | Verification / remaining work |
|---|---|---|
| Small uploaded MP4 | Inline Gemini video extraction, learned retrieval and cited recap | Real six-second red/blue clip passed; two correctly timestamped observations, generated recap and review after restart |
| Recorded YouTube | Bounded direct URL analysis | `S_9wb3g7jtY` 05:00–08:00 passed: seven observations and cited recap awaiting review; no upload. The later Safari demo returned eight observations on the same interval. These are separate runs on one source/window; [original test](../reports/youtube-interval-test.md), [demo rerun](../reports/safari-demo.md) |
| Large upload | Files API processing path | Earlier processing returned HTTP 500; larger-upload end-to-end success remains unverified |
| Agent decisions | Bounded Gemini retrieve/inspect/summarize/clarify graph, fallback and call budgets | Real small-video graph passed; 38 Python tests pass across product, observability, evaluation, judge and Streamlit integration checks; provider responses are fixtures in these tests |
| Summary grounding | Evidence IDs, separate model check, explicit extractive fallback | Integration passed; independent race factual review still needed |
| Semantic retrieval | Learned Gemini Embedding 2 vectors and strict time filters | Real generation and 768-dimensional embedding checks passed |
| Durable review | LangGraph interrupt and SQLite checkpoints | Automated and real-provider recap review resumed after restart |
| Background jobs / accounts | Persistent local login, account isolation, leases, cancellation and recovery | Local contract and Streamlit tests pass |
| Live capture | Continuous public YouTube segments, explicit coverage and last-15-minute query | Active race-stream test deferred at the user's request; clock alignment remains unmeasured |
| Real evaluation | Human annotation screen and aggregation command | No independently reviewed race dataset yet; no real-race quality score claimed |
| Tracing | Local traces and selectable Braintrust/LangSmith spans | Braintrust parent/retrieval/Nebius delivery was verified by server-side readback; the fresh Safari video trace was also inspected in the hosted UI. The last saved LangSmith check returned HTTP 429; it was not retested in this review. [Evidence](../reports/safari-demo.md) |
| Nebius judge | Separate Qwen judge against supplied reference facts | Five real authored-fixture calls: 4/5 agreement, one disagreement retained. Independent human calibration remains pending |
| Week 5 lab | Separate local LoRA intent classifier and Streamlit demo | 96-step loss curves, five correct merge smoke examples, 27.5% / 52.5% / 70% comparison; no production video-quality benefit claimed |
| Public hosting | Docker/Caddy/OIDC configuration and backup script | Deferred: local product first. Container build and hosted authentication are unverified |

The default generation model is `gemini-3.5-flash`. Small MP4s up to 12 MB use inline input; larger files use the provider Files API. An API key alone does not guarantee access to every model or video source. There is no automatic bypass of unavailable/restricted video.

The original evidence demo remains the dependable key-free presentation path: **17 tests and 40/40 synthetic cases**, versus 20/40 for naive overlap. The separate BERT-tiny LoRA lab reached 70% on authored held-out requests; it is not deployed as the planner.

## Finish validation

1. Analyze short race MP4s and independently review at least 10 varied intervals in Evaluation.
2. Expand the successful YouTube interval check to varied sources; recheck the earlier failed URL and Files API.
3. Test a currently live public race stream when one is available.
4. Build the reviewed video evaluation and calibrate the judge. Braintrust already demonstrates hosted delivery; obtain LangSmith-specific evidence if following that exact handout requirement.

See [setup](setup.md) for exact account and launch steps, and [verification](../reports/verification.md) for test scope.

## Week 4 evaluation follow-through

[Independent labels, judge calibration and controlled abstention experiments](https://github.com/sivalinb/racetime-copilot/blob/main/docs/week4-evaluation.md): the reviewer form and analysis tools now retain unanswerable cases, distinguish unnecessary refusals from unsupported answers, preserve review revisions and analyze paired 2×2 runs. Missing study evidence blocks readiness; complete inputs still require manual release review. Independent video labels, calibrated judge results and real interaction runs remain pending. Earlier feedback is not presented as a RaceTime experiment result.

## Nebius judge and Week 5 demo

[Nebius and Braintrust guide](https://github.com/sivalinb/racetime-copilot/blob/main/docs/nebius-braintrust.md): optional Nebius judge implemented and tested with five real provider calls (4/5 authored-fixture agreement; one disagreement retained). Braintrust parent/retrieval/Nebius spans were verified by server-side readback; [recorded proof](https://github.com/sivalinb/racetime-copilot/blob/main/evals-observability/observability/examples/braintrust-nebius-check.json). [Week 5 demonstration](https://github.com/sivalinb/racetime-copilot/blob/main/docs/week5-demonstration.md) includes the measured loss curve, five correct smoke examples, baseline comparisons and live local router. Independent judge calibration and custom submission remain pending.
