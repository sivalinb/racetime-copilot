"""No-network checks for judge safety, strict verdicts and Braintrust nesting."""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from racetime.judge import JudgeCase, judge
from racetime.observability import current_span, metadata, record, span, trace_reference

ROOT = Path(__file__).resolve().parents[1]


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.case = JudgeCase.model_validate(
            json.loads(
                (
                    ROOT / "evals-observability/datasets/nebius-judge-smoke-v1.json"
                ).read_text()
            )["cases"][0]["input"]
        )
        self.session = MagicMock()
        self.response = self.session.post.return_value
        self.response.status_code = 200
        self.verdict = {
            "factual_support": True,
            "completeness": True,
            "response_appropriate": True,
            "temporal_compliance": True,
            "explanation": "Fixture reference supports abstention.",
            "issues": [],
        }
        self.response.json.return_value = {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps(self.verdict)},
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

    def test_schema_usage_and_no_key_in_result(self):
        with patch.dict(
            os.environ,
            {"NEBIUS_API_KEY": "private-test-key", "RACETIME_OBSERVABILITY": "none"},
        ):
            result = judge(self.case, session=self.session)
        self.assertTrue(result["judge_accept"])
        self.assertEqual(result["usage"]["total_tokens"], 15)
        self.assertNotIn("private-test-key", json.dumps(result))
        args = self.session.post.call_args.kwargs
        self.assertFalse(args["allow_redirects"])
        self.assertEqual(args["json"]["max_tokens"], 1800)
        self.assertNotIn("human_accept", args["json"]["messages"][1]["content"])

    def test_http_failure_is_not_a_score(self):
        self.response.status_code = 429
        with patch.dict(
            os.environ,
            {"NEBIUS_API_KEY": "private-test-key", "RACETIME_OBSERVABILITY": "none"},
        ):
            with self.assertRaisesRegex(ValueError, "HTTP 429"):
                judge(self.case, session=self.session)

    def test_truncated_and_malformed_responses_fail(self):
        with patch.dict(
            os.environ, {"NEBIUS_API_KEY": "test", "RACETIME_OBSERVABILITY": "none"}
        ):
            self.response.json.return_value["choices"][0]["finish_reason"] = "length"
            with self.assertRaises(ValueError):
                judge(self.case, session=self.session)
            self.response.json.return_value["choices"][0] = {
                "finish_reason": "stop",
                "message": {"content": "{}"},
            }
            with self.assertRaises(ValueError):
                judge(self.case, session=self.session)

    def test_braintrust_nesting_and_tokens(self):
        logger = MagicMock()
        root = logger.start_span.return_value
        root.id = "root-id"
        child = root.start_span.return_value
        child.id = "child-id"
        child.link.return_value = "https://www.braintrust.dev/test"
        with (
            patch.dict(os.environ, {"RACETIME_OBSERVABILITY": "braintrust"}),
            patch("racetime.observability.braintrust_logger", return_value=logger),
        ):
            with span("job") as parent:
                with span("model", "llm") as run:
                    self.assertIs(current_span(), run)
                    record(
                        run,
                        {
                            "usage_metadata": {
                                "input_tokens": 10,
                                "output_tokens": 5,
                                "total_tokens": 15,
                            }
                        },
                    )
                    metadata(run, {"model": "fixture"})
                    ref = trace_reference(run)
                    self.assertEqual(ref["root_run_id"], parent.id)
                    self.assertEqual(ref["provider"], "braintrust")
            self.assertIsNone(current_span())
        self.assertEqual(child.log.call_args_list[0].kwargs["metrics"]["tokens"], 15)
        child.end.assert_called_once()
        root.end.assert_called_once()

    def test_braintrust_outage_preserves_application_and_sanitizes_error(self):
        with (
            patch.dict(os.environ, {"RACETIME_OBSERVABILITY": "braintrust"}),
            patch(
                "racetime.observability.braintrust_logger",
                side_effect=RuntimeError("SECRET"),
            ),
        ):
            with span("job") as run:
                self.assertIsNone(run)
        logger = MagicMock()
        with (
            patch.dict(os.environ, {"RACETIME_OBSERVABILITY": "braintrust"}),
            patch("racetime.observability.braintrust_logger", return_value=logger),
        ):
            with self.assertRaisesRegex(ValueError, "SECRET"):
                with span("job"):
                    raise ValueError("SECRET")
        self.assertNotIn("SECRET", str(logger.start_span.return_value.log.call_args))


if __name__ == "__main__":
    unittest.main()
