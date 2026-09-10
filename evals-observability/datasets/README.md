# Data and golden expectations

## Evidence golden v1

[evidence-golden-v1.json](evidence-golden-v1.json) freezes the project's existing 40 authored synthetic cases. Each case contains `id`, `name`, `q` (question and time bounds), `events` (source observations) and `expected` (the exact evidence IDs that should remain).

| Group | Cases | Expected behavior |
|---|---:|---|
| Exact cue containment | 16 | Include the fully contained cue |
| Cue crosses interval end | 16 | Exclude a partially overlapping cue |
| Opening, gap, conflict, later, finish hidden/visible | 6 | Match the authored evidence selection for each scenario |
| Delayed availability | 1 | Exclude evidence unavailable at the cutoff |
| Instruction embedded in source text | 1 | Exclude the known suspicious instruction fixture |

These cases were authored within this project from fictional Canyon Relay observations. They are not an external dataset, an independent blind test, or proof of general prompt-injection resistance. The conflict case checks selected IDs; the trace demo separately checks that a conflict is flagged. Retry and cache behavior are separate checks, not extra golden cases.

The v1 runner reads saved expectations without deriving them from the candidate. [manifest.json](manifest.json) pins the exact dataset bytes with SHA-256. To change golden expectations, review the reason, create a new version and manifest entry, and keep the old version for comparison. Do not change expected answers just to make a regression pass. Checksums detect file changes; they do not certify labeling quality.

## Routing train/test v1

[router-v1.json](router-v1.json) contains **144 training requests and 40 held-out requests**, balanced across `recap`, `runner`, `verify` and `compare`. Training uses authored templates; test wording was authored separately. It is one synthetic split, not independently labeled real-user data.

The [recorded result](../benchmarks/router-recorded.json) contains every held-out prediction, per-class metrics, a confusion matrix and `dataset_sha256`, which matches this file. Held-out requests do not enter optimizer updates. Avoid tuning repeatedly against this same test split; collect a new blind set for further selection. Reproduction code is in [the routing lab](../../training/README.md).

## Real-video ground truth

There is **no published independently reviewed race dataset yet**. The red/blue provider integration example is synthetic video; neither its model observations nor an approved recap should be promoted to ground truth.

1. Use authorized race footage and choose an interval. Write expected facts and source timestamps independently of the model's answer.
2. After generating a recap, open **Video workspace → Evaluation** and confirm that you watched the interval.
3. Record expected facts, supported-sentence percentage, missed important events, spoiler leaks and largest timestamp error. Save and download the annotation.
4. Annotations remain under ignored `.runtime/evaluations/<owner>/<job>.json`. Saving again for the same job replaces that annotation. Keep a separate reviewed dataset if multiple reviewers or revisions are needed.
5. Aggregate saved annotations from the repository root:

```bash
python scripts/evaluate_real.py
```

The command refuses to produce a benchmark when no reviewed cases exist. It reports case/reviewer count, mean reviewer-entered supported percentage, total misses/leaks and largest timestamp error. The mean is per-case, not weighted by sentence count. Scores are human judgments; the program does not independently certify them.

[human-review-template.json](human-review-template.json) documents the annotation fields with empty values. It is not a labeled example and must not be counted as an evaluated case. Before claiming real-race quality, use varied footage, more than one reviewer where possible, resolve disagreements, and reserve a blind test set.
