"""Tracing must preserve results and never serialize provider secrets/media."""

import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

os.environ["LANGSMITH_TRACING"] = "false"

from racetime.observability import observed, span


class ObservabilityTests(unittest.TestCase):
    def test_real_graph_emits_nested_model_and_tool_payloads(self):
        import langsmith as ls

        from racetime.provider import Gemini
        from racetime.service import Service
        from racetime.store import Store
        from scripts.check_langsmith import FixtureModels

        client = ls.Client(
            api_key="test", api_url="http://localhost:1", auto_batch_tracing=False
        )
        payloads = {}

        def create(*args, **kwargs):
            payloads[str(kwargs["id"])] = dict(kwargs)

        def update(run_id, **kwargs):
            payloads[str(run_id)].update(
                {k: v for k, v in kwargs.items() if v is not None}
            )

        with (
            tempfile.TemporaryDirectory() as folder,
            patch.dict(
                os.environ,
                {
                    "LANGSMITH_TRACING": "true",
                    "LANGSMITH_API_KEY": "test",
                },
            ),
            patch.object(ls.Client, "create_run", side_effect=create),
            patch.object(ls.Client, "update_run", side_effect=update),
            patch(
                "langsmith.run_trees.RunTree.get_url",
                return_value="https://smith.langchain.com/test",
            ),
            patch("racetime.agent.DATA", Path(folder)),
            ls.tracing_context(client=client, enabled=True),
        ):
            store = Store(Path(folder) / "db.sqlite")
            service = Service(
                store,
                lambda *args: Gemini(
                    *args, client=SimpleNamespace(models=FixtureModels())
                ),
            )
            media = service.add_video(
                "test", "fixture", "https://www.youtube.com/watch?v=S_9wb3g7jtY"
            )
            job_id = service.enqueue(
                "test",
                "recap",
                {
                    "media": media["id"],
                    "start": 0,
                    "end": 30,
                    "as_of": 30,
                    "question": "Synthetic check",
                },
            )
            service.process_one()
            job = store.job("test", job_id)
            self.assertEqual(job["status"], "awaiting_review")
            root_id = job["result"]["observability"]["run_id"]
            service.review("test", job_id, "rejected")
            self.assertEqual(store.job("test", job_id)["status"], "completed")
        client.flush()
        root = payloads[root_id]
        self.assertEqual(root["outputs"]["status"], "awaiting_review")
        children = [
            r
            for r in payloads.values()
            if str(r.get("trace_id")) == root_id and str(r["id"]) != root_id
        ]
        self.assertTrue(
            {"llm", "tool", "retriever", "embedding"}
            <= {r["run_type"] for r in children}
        )
        llms = [r for r in children if r["run_type"] == "llm"]
        self.assertEqual(len(llms), 4)
        for run in llms:
            self.assertIsNotNone(run.get("parent_run_id"))
            self.assertEqual(run["outputs"]["usage_metadata"]["total_tokens"], 15)
            self.assertNotIn("parts", run["inputs"])
            self.assertNotIn("self", run["inputs"])

    def test_telemetry_setup_failure_preserves_result(self):
        with (
            patch("racetime.observability.enabled", return_value=True),
            patch(
                "racetime.observability.ls.trace", side_effect=RuntimeError("offline")
            ),
        ):
            with span("test") as run:
                self.assertIsNone(run)

    def test_only_explicit_inputs_are_logged(self):
        manager = MagicMock()
        manager.__enter__.return_value.outputs = {}

        @observed("example", "tool", ("question",))
        def action(question, secret, video):
            return "done"

        with (
            patch("racetime.observability.enabled", return_value=True),
            patch("racetime.observability.ls.trace", return_value=manager) as traced,
        ):
            self.assertEqual(action("recap", "SECRET", b"VIDEO"), "done")
        self.assertEqual(traced.call_args.kwargs["inputs"], {"question": "recap"})

    def test_failure_message_is_sanitized_and_original_raised(self):
        manager = MagicMock()
        with (
            patch("racetime.observability.enabled", return_value=True),
            patch("racetime.observability.ls.trace", return_value=manager),
        ):
            with self.assertRaisesRegex(ValueError, "SECRET"):
                with span("provider"):
                    raise ValueError("SECRET")
        error = manager.__enter__.return_value.end.call_args.kwargs["error"]
        self.assertNotIn("SECRET", error)
        manager.__exit__.assert_called_once_with(None, None, None)

    def test_transport_exit_failure_does_not_override_app_error(self):
        manager = MagicMock()
        manager.__exit__.side_effect = RuntimeError("transport")
        with (
            patch("racetime.observability.enabled", return_value=True),
            patch("racetime.observability.ls.trace", return_value=manager),
        ):
            with self.assertRaisesRegex(ValueError, "application"):
                with span("example"):
                    raise ValueError("application")


if __name__ == "__main__":
    unittest.main()
