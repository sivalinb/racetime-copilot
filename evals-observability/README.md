# Evals and observability

Start here to see **what we test, what the data contains, what passed, and how a run can be inspected**.

## What is demonstrated

| Evidence | Benchmark / status | Scope |
|---|---|---|
| [Frozen evidence benchmark](benchmarks/evidence-latest.json) | 40/40 cases; naive baseline 20/40 | Exact evidence selection on authored synthetic cases |
| [Routing experiment](benchmarks/router-recorded.json) | Accuracy 52.5% → 70%; macro F1 0.522 → 0.709 | Separate BERT-tiny LoRA classifier; not deployed |
| [Trace examples](observability/examples/evidence-demo.json) | Conflict, failed retrieval, recovery and cache hit | Actual local runs using fictional race observations |
| [Video integration record](observability/examples/video-integration-recorded.json) | Six-second red/blue clip, cited recap and review after restart | Real Gemini integration on synthetic video; not race accuracy |
| [Direct YouTube interval test](../reports/youtube-interval-test.md) | 05:00–08:00; seven observations and cited recap awaiting review | Real public race-discussion video; integration only, no human accuracy score |
| [Real-video evaluation process](datasets/README.md#real-video-ground-truth) | Annotation UI and aggregation implemented | No independently reviewed real-race benchmark published |
| [External observability](observability/README.md#langsmith) | Explicit job/model/tool spans and Streamlit links; [instrumentation check](observability/langsmith-check.md) | Local SDK payload tests pass; hosted ingestion still blocked by monthly HTTP 429 |

## Run the golden benchmark

For useful next test candidates, browse [100 YouTube questions and scenarios](../docs/youtube-question-library.md) and their [structured catalog](datasets/youtube-question-scenarios-v1.json). Every case is marked `not_run`, with `ground_truth: null`. This is a prompt library, separate from the frozen golden benchmark and its scores.

From the repository root, after installing Node.js 22.13+:

```bash
npm ci
npm run eval:benchmark
```

No API key is needed. The command reads the **fixed** [golden dataset](datasets/evidence-golden-v1.json), checks its checksum, runs the current workflow and compares every result with the saved expected evidence IDs. It writes per-case results, latency percentiles, code hashes and trace examples. It exits nonzero if a case or observability check fails. GitHub Actions runs the same command and uploads the reports as the **evidence-benchmark** artifact.

The original `npm run eval` remains available. It generates its cases from the original script; this new command consumes the frozen v1 file instead. A benchmark run never regenerates its golden answers.

## Folder guide

| Folder | Contents |
|---|---|
| [datasets](datasets/README.md) | Golden inputs/expected IDs, routing train/test data, provenance, checksums and a blank human-review template |
| [benchmarks](benchmarks/README.md) | Per-case evidence results, baseline comparison, recorded routing metrics and limitations |
| [observability](observability/README.md) | Trace fields, demo steps, usage tracking, LangSmith status and sample runs |
| [run.ts](run.ts) | Reproducible evidence benchmark and conflict/retry/cache checks |

## Five-minute demonstration

1. Run `npm run eval:benchmark`; show 40/40 versus 20/40 and the four trace checks.
2. Open `datasets/evidence-golden-v1.json`. Compare one `contained-*` case with its `clipped-*` case: crossing the boundary changes the expected result to empty.
3. Open `benchmarks/evidence-latest.json`; match that case's `expected`, `actual`, `baseline` and `pass` fields.
4. In Streamlit **Evidence demo**, request Canyon Relay `00:00–15:00`. Open **Inspect this run’s trace**, show the conflicting claims, simulate one retrieval failure, then repeat the same request to show a cache hit.
5. Open **Capstone learning** for the original evaluation summaries. In **Video workspace**, an existing result's JSON shows the model/rule decisions; **Evaluation** lets a reviewer score it after watching the source.

## What the scores do not establish

The 40 cases test deterministic evidence handling, not generated-summary factual accuracy. The routing lab uses one small synthetic split and one seed. Local millisecond timings exclude video processing and network calls. One direct YouTube interval passed integration; an earlier different URL and Files API processing failed. Active livestream validation is pending, and LangSmith quota was exhausted. See [current product status](../docs/product-status.md).

Private videos, accounts, credentials and runtime traces stay outside this folder. Only fictional data and already-public integration examples are committed.

## Course evidence

See the [Week 1–5 handout audit](../docs/course-completion-audit.md) for the difference between demonstrated learning and completed assignments. Week 4 is partial: the frozen synthetic benchmark and local traces do not replace independently reviewed video cases, verified LangSmith model/tool child runs or 3–4 measured improvements. The 100 questions are candidate scenarios, not completed evals.
