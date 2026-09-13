"""Regression coverage for abstention, calibration and paired comparisons."""

import unittest

from racetime.evaluation import (
    calibrate_judge,
    interaction_report,
    summarize_annotations,
)


def annotation(**overrides):
    return {
        "reviewer": "fixture-reviewer",
        "independently_reviewed": True,
        "answerability": "unanswerable",
        "response_type": "abstain",
        "expected_facts": [],
        "label_reason": "Fixture interval has no winner announcement.",
        "supported_percent": None,
        "unsupported_claims": 0,
        "missed_events": 0,
        "spoiler_leaks": 0,
        "max_timestamp_error_s": 0,
        **overrides,
    }


class EvaluationTests(unittest.TestCase):
    def test_unanswerable_empty_facts_retained_without_fake_accuracy(self):
        result = summarize_annotations([annotation()])
        self.assertEqual(result["count"], 1)
        self.assertIsNone(result["mean_supported_percent"])
        self.assertEqual(result["unanswerable_case_count"], 1)

    def test_opposing_failure_types_remain_visible(self):
        result = summarize_annotations(
            [
                annotation(
                    answerability="answerable", expected_facts=["00:05: runner arrives"]
                ),
                annotation(
                    response_type="answer", supported_percent=0, unsupported_claims=2
                ),
            ]
        )
        self.assertEqual(result["unnecessary_abstentions"], 1)
        self.assertEqual(result["answers_on_unanswerable"], 1)
        self.assertEqual(result["unsupported_claims"], 2)

    def test_legacy_and_invalid_scores_are_explicitly_excluded(self):
        result = summarize_annotations(
            [{}, annotation(response_type="answer", supported_percent=float("nan"))]
        )
        self.assertEqual(result["count"], 0)
        self.assertEqual(len(result["excluded"]), 2)
        self.assertEqual(result["release_status"], "not_established")

    def test_calibration_exposes_false_accepts(self):
        result = calibrate_judge(
            [
                {"id": "a", "human_accept": False, "judge_accept": True},
                {"id": "b", "human_accept": True, "judge_accept": True},
            ]
        )
        self.assertEqual(result["agreement"], 0.5)
        self.assertEqual(result["false_accept_rate"], 1)
        self.assertEqual(result["disagreement_ids"], ["a"])
        self.assertTrue(result["both_label_classes_present"])
        self.assertIsNone(calibrate_judge([])["agreement"])

    def test_calibration_rejects_missing_and_duplicate_labels(self):
        with self.assertRaises(ValueError):
            calibrate_judge([{"id": "a", "human_accept": None, "judge_accept": True}])
        row = {"id": "a", "human_accept": False, "judge_accept": False}
        with self.assertRaises(ValueError):
            calibrate_judge([row, row])

    def test_interaction_requires_same_pairs_not_just_same_counts(self):
        rows = [
            {
                "case_id": "a",
                "repeat": 1,
                "retrieval": r,
                "policy": p,
                "passed": r == p == "candidate",
            }
            for r in ("current", "candidate")
            for p in ("current", "candidate")
        ]
        result = interaction_report(rows)
        self.assertEqual(result["interaction_difference"], 1)
        rows[-1]["case_id"] = "b"
        result = interaction_report(rows)
        self.assertFalse(result["paired_complete"])
        self.assertIsNone(result["interaction_difference"])
        with self.assertRaises(ValueError):
            interaction_report([rows[0], rows[0]])


if __name__ == "__main__":
    unittest.main()
