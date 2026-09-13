# Submission review

Reviewed on **12 September 2026** against published application commit `57cdffdc3fc0e5c606b51b2da9b280a136f9a3b9`, the original Week 1–5 handouts, saved results and the actual Safari demo. This is a project self-review, not instructor acceptance.

## Submission materials

| Item | Status |
|---|---|
| [Public GitHub repository](https://github.com/sivalinb/racetime-copilot) | Implementation, instructions, benchmark data and supporting reports available |
| [Product Google Doc and learning map](https://docs.google.com/document/d/1ydt7QpdRq_rzFGqsOr2n1GnYuIbHeCK2TPiUQ9X-h6M/edit) | Product introduction, architecture, comparison, Week 1–5 evidence table and current limits; anyone with the link can view |
| Five-minute Safari MP4 and subtitles | Prepared locally on Desktop; [flow and evidence](safari-demo.md). Attach/share the video for the instructor; no hosted recording URL is claimed |
| AI-assisted development evidence | Actual coding-prompt screenshots, iterations and lessons still need packaging for the Week 1/3 handout requirements |
| Final hand-in | Not submitted by this review; custom-format/instructor acceptance is not established |

## Claims checked

| Claim | Evidence and limit |
|---|---|
| Direct YouTube analysis works without upload | [Original integration](youtube-interval-test.md): seven observations. [Safari rerun](safari-demo.md): eight. Same source and interval; both await independent factual review |
| Hosted observability is demonstrated | Braintrust [fixture readback](../evals-observability/observability/examples/braintrust-nebius-check.json) and [fresh video trace inspected in Safari](safari-demo.md). The historical LangSmith failure is not a current quota measurement |
| Nebius is an evaluation judge | [Five real provider requests](../evals-observability/benchmarks/nebius-judge-smoke-recorded.json), 4/5 authored-fixture agreement, one false rejection retained. Not independently calibrated |
| Golden evidence benchmark | [40/40 versus 20/40](../evals-observability/benchmarks/evidence-latest.json) on frozen synthetic evidence-ID cases; not video-answer accuracy |
| LoRA specialization | [Current report](router-evaluation.json): 27.5% untrained head, 52.5% trained head/frozen encoder, 70% LoRA; 96 updates and 12 held-out errors. [Five merge smoke examples](router-smoke.json) pass |
| 100 YouTube scenarios | Authored [question catalog](../evals-observability/datasets/youtube-question-scenarios-v1.json), marked `not_run` with null ground truth; not 100 evaluated cases |
| Test coverage | 38 Python tests and 17 TypeScript tests passed in this review; TypeScript checking and Ruff lint/format checks passed. Fixture-based tests do not measure provider accuracy |
| Differentiation | A race-focused workflow and inspectable engineering; [provider comparison](../docs/product-positioning.md) does not claim a new model capability or measured superiority |

## Remaining learning and product validation

The original handouts permit custom applications. The separate BERT-tiny LoRA lab demonstrates an adapted Week 5 workflow; it is not the supplied Qwen3/LLaMA Factory exercise. Week 4 explicitly names LangSmith evidence. Braintrust demonstrates the observability concept but does not establish acceptance of a platform substitution.

Independent source labels, judge calibration, a video-agent baseline and measured improvements remain open. Active-stream validation, long-duration reliability and production hosting remain unverified. These limits are disclosed rather than represented as completed learning or product validation.

Historical reports retain their original observations, failures and counts. Current guides distinguish those runs from the later demo and current tests.

The frozen benchmark was rerun without changing its dataset or historical reports: 40/40 versus 20/40, with conflict, retry, recovery and cache checks passing. All 126 unique local repository link targets checked across 25 guides/reports existed. The competitor descriptions were checked against their linked provider pages; they remain descriptions of published features, not comparative performance measurements. The previously removed interview references, named inspiration reference and image-prompt documents are absent from the current published-source candidate.
