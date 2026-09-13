# Week 4 evaluation tooling check

Status: tooling verified locally; independent real-video study remains pending.

- 33 Python tests passed, including six evaluation regression tests and the Streamlit account/queue/evaluation integration test.
- An unanswerable response with no expected facts is retained; its supported-sentence percentage is null.
- Unsupported answers and unnecessary abstentions are counted separately.
- Missing legacy fields and non-finite scores produce explicit exclusions.
- Calibration exposes false acceptances and disagreement IDs; missing/duplicate judgments are rejected.
- Interaction calculations require identical case/repeat pairs in all four cells; duplicate runs are rejected.
- Streamlit saves an empty-fact unanswerable annotation and preserves the earlier review on a second save.
- The empty study template produces a blocked report and nonzero exit, not a fabricated score or release approval.
- Ruff formatting and lint checks pass.

These are automated fixture tests, not independent human labels, a calibrated judge, measured video accuracy, or a completed ablation experiment. No provider calls were made for these checks. The deployed answerability policy is unchanged; clarification traces now expose the existing decision reason and evidence count.

See [the protocol](../../docs/week4-evaluation.md), [tests](../../tests/evaluation_test.py) and [Streamlit integration](../../tests/video_ui_test.py).
