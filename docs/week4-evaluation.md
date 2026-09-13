# Week 4: measure when to answer and when to abstain

RaceTime should answer what the allowed video interval supports, give a partial answer when evidence is incomplete, and explain when the answer is unavailable. Refusing an answerable question is also a failure.

**Current status:** evaluation tooling is implemented; independent video labels, calibrated judge results and repeated real-video interaction experiments are pending. The existing 40 synthetic cases and successful YouTube integration do not fill those gaps. The Week 4 feedback describes an earlier evaluation; its negative result and causal findings are not RaceTime results.

| Feedback | How RaceTime incorporates it | What still requires evidence |
|---|---|---|
| Keep negative results visible | Study reports preserve raw inputs, code/model versions, dataset hash, per-case passes and failures. Existing output paths cannot be overwritten. | Actual baseline and candidate runs, including failed candidates |
| Complete independent labels | Evaluation form records answerability, timestamped expected facts, source rationale, reviewer and whether labels were prepared before viewing the model answer. Unanswerable cases may have empty facts. Earlier reviews are preserved. | Independent reviewers, blind labels, disagreements and adjudication |
| Calibrate the judge | Calibration analysis reports human/judge confusion counts, agreement, false acceptance and disagreement IDs. Missing judgments are rejected. | Frozen rubric, calibration split and held-out judge check |
| Repeat interaction tests | Paired 2×2 analysis compares current/candidate retrieval with current/candidate answerability policy. It refuses to calculate an interaction when case/repeat pairs differ. | Repeated real runs, controlled settings and uncertainty analysis |
| Block release despite faster or safer behavior | Incomplete study reports are marked blocked. Complete inputs still require manual review against predeclared quality bars. Speed cannot override failed quality. | Reviewed release criteria and a signed decision; this is not an automated production deployment gate |

## 1. Prepare source labels before seeing answers

Start with 30–50 varied questions from several authorized videos, including answerable, partially answerable and unanswerable questions. The 100-question catalog supplies candidates, not golden labels. Include unclear audio, missing camera coverage, contradictory commentary, interval boundaries and questions about results outside the spoiler cutoff.

For each case, save a stable case ID, video URL, interval, cutoff, source snapshot/version, expected facts with timestamps, answerability and the reason. An unanswerable case needs a reason, not a fabricated fact. Two reviewers should independently label at least a varied subset without seeing each other's labels or model answers. Save both originals, report agreement and disagreements, and record the adjudicator's resolution. Self-attesting that the source was watched is not proof of blind independent labeling.

Split by source video/event into development, judge calibration and held-out evaluation sets so neighboring clips do not leak across splits. Freeze labels and version the dataset before candidate comparisons. Do not tune repeatedly on the held-out set.

In **Video workspace → Evaluation**, select a result and record the actual response type separately from source answerability. Enter unsupported claims, missed events, spoilers and timestamp errors. For abstentions, supported-sentence percentage is not applicable; it is saved as null. Partial answers still need review of both supported statements and omissions.

## 2. Calibrate an evaluation judge

Use a written rubric: factual statements must match source-reviewed facts, citations must support their specific claims, time boundaries must hold, and the answer must address the question. An abstention is appropriate only where the available source cannot answer; partial coverage should not justify inventing missing events.

Ask a judge to score the frozen responses without knowing which configuration produced them. Compare with human labels, inspect false acceptances and false rejections, refine the rubric only on calibration data, and freeze it before the held-out check. A different model may reduce shared errors but does not replace human calibration. RaceTime's current generation-time grounding check uses the same configured model and is not this independent evaluation judge.

## 3. Run ablations and interactions

First isolate each suspected cause: keep retrieval fixed while changing answerability policy, then keep policy fixed while changing retrieval. The full design is:

| Configuration | Retrieval | Answerability policy |
|---|---|---|
| Baseline | Current | Current |
| Retrieval only | Candidate | Current |
| Policy only | Current | Candidate |
| Combined | Candidate | Candidate |

Use the same case IDs and repeat numbers in all four cells; aim for at least three repeats initially. Keep observations/source snapshots, model, budgets and unrelated prompts fixed. Record extraction changes as a separate experiment. Analyze per-case regressions as well as aggregate pass rates. The script's difference of differences is descriptive; clustered uncertainty estimates and enough independent source videos are needed before drawing strong conclusions. Do not change retrieval or the production abstention policy solely because a theory sounds plausible.

## 4. Decide whether a candidate is ready

Before running comparisons, write numerical quality bars and minimum sample sizes in the study's release criteria. Track factual support, unsupported claims, missed facts, inappropriate answers, unnecessary abstentions, spoiler leaks, timestamp errors and performance separately. Do not count a refusal as automatically safe or correct. Preserve a failed release decision even if latency or one safety metric improves. Approving one recap in the app is separate from approving a model/prompt release.

Record the decision, responsible reviewer, dataset/code/model/rubric versions, failed cases and the next hypothesis. There is no independently established real-video release pass yet.

## Run the tools

From the repository root, with Python dependencies installed:

```bash
python scripts/evaluate_real.py
python scripts/evaluate_week4.py --input path/to/reviewed-study.json
```

The first command summarizes local annotations and fails on missing/invalid annotations. Old records without explicit answerability must be reviewed and migrated; the script lists exclusions instead of silently assigning labels. Counts are annotations, not deduplicated independent cases; adjudicate repeated reviews before a benchmark.

The second reads a study in the [study template format](https://github.com/sivalinb/racetime-copilot/blob/main/evals-observability/datasets/week4-study-template.json), computes judge calibration and paired interactions, and saves a timestamped report under ignored `.runtime/week4/`. It analyzes supplied results; it does not call a provider, recruit reviewers or run candidate agents. Empty templates produce a blocked report and a nonzero exit. Metadata and human scores are supplied attestations, not automatically certified evidence. A complete report requires manual release review.

## Evidence and observability

[Evaluation implementation](https://github.com/sivalinb/racetime-copilot/blob/main/racetime/evaluation.py) · [Regression tests](https://github.com/sivalinb/racetime-copilot/blob/main/tests/evaluation_test.py) · [Human review template](https://github.com/sivalinb/racetime-copilot/blob/main/evals-observability/datasets/human-review-template.json) · [Existing benchmarks](https://github.com/sivalinb/racetime-copilot/tree/main/evals-observability/benchmarks)

The agent trace records planner mode and decision, selected evidence, inspection and whether output used verified generation, an extractive fallback or clarification. Clarification traces now include a reason code and evidence count. Link each experiment run to its local or hosted trace in the study record. LangSmith delivery remains subject to the configured workspace quota; adding another tracing service does not supply human labels or calibrate a judge.
