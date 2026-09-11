"""Account and queue UI against temporary SQLite, without provider calls."""

import os
import sys
import tempfile
import unittest

os.environ["LANGSMITH_TRACING"] = "false"
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from racetime.service import Service
from racetime.store import Store

ROOT = Path(__file__).resolve().parents[1]


class VideoUI(unittest.TestCase):
    def test_account_and_video_queue(self):
        with tempfile.TemporaryDirectory() as folder:
            svc = Service(Store(Path(folder) / "test.sqlite"))
            with (
                patch("racetime.ui.service", return_value=svc),
                patch("racetime.ui.configured", return_value=True),
            ):
                at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
                at.radio(key="workspace_mode").set_value("Video workspace").run()
                self.assertFalse(at.exception)
                next(s for s in at.selectbox if s.label == "Account action").select(
                    "Create account"
                )
                next(t for t in at.text_input if t.label == "Username").set_value(
                    "runner-test"
                )
                next(
                    t for t in at.text_input if t.label.startswith("Password")
                ).set_value("A strong test password")
                next(b for b in at.button if b.label == "Continue").click().run()
                self.assertFalse(at.exception)
                next(t for t in at.text_input if t.label == "Video title").set_value(
                    "Test race"
                )
                next(
                    t for t in at.text_input if t.label == "Public YouTube URL"
                ).set_value("https://www.youtube.com/watch?v=qnVos4_1soM")
                next(b for b in at.button if b.label == "Save video").click().run()
                self.assertFalse(at.exception)
                next(b for b in at.button if b.label == "Queue job").click().run()
                self.assertFalse(at.exception)
                owner = at.session_state["video_user"]
                jobs = svc.store.jobs(owner)
                self.assertEqual(jobs[0]["status"], "queued")
                next(b for b in at.button if b.label == "Cancel job").click().run()
                self.assertTrue(svc.store.job(owner, jobs[0]["id"])["cancel"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
