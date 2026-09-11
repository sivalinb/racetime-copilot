"""Exercise the real Streamlit application against the running local backend."""

import json
from pathlib import Path
from uuid import uuid4

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
assert not at.exception, at.exception
assert any("Pick a moment" in item.value for item in at.title)
next(b for b in at.button if b.label == "Create recap").click().run()
assert not at.exception, at.exception
run = at.session_state["run"]
assert run["status"] == "needs_review"
assert [c["ids"] for c in run["conflicts"]] == [["E05", "E06"]]
assert "E09" not in [f["id"] for f in run["findings"]]
at.button(key="approved").click().run()
assert at.session_state["run"]["review"] == "approved"
at.text_input(key="range_start").set_value("15:00")
at.text_input(key="range_end").set_value("20:00")
at.text_input(key="range_cutoff").set_value("15:00")
next(b for b in at.button if b.label == "Create recap").click().run()
assert len(at.error) > 0
at.text_input(key="range_cutoff").set_value("20:00")
at.text_input(key="question").set_value("What happened? " + uuid4().hex)
at.checkbox(key="simulate_failure").check()
next(b for b in at.button if b.label == "Create recap").click().run()
assert not at.exception, at.exception
run = at.session_state["run"]
assert [f["id"] for f in run["findings"]] == ["E09", "E10"]
assert [t["status"] for t in run["trace"] if t["name"] == "retrieve"] == ["retry", "ok"]
at.text_input(key="import_title").set_value(
    "Streamlit test - synthetic imported evidence"
)
at.text_area(key="import_text").set_value(
    "WEBVTT\n\n00:00:10.000 --> 00:00:20.000\nSynthetic runner at the checkpoint."
)
next(b for b in at.button if b.label == "Import source").click().run()
assert not at.exception, at.exception
assert any("Saved Streamlit test" in item.value for item in at.success)
options = at.selectbox(key="source_select").options
assert any("Streamlit test" in title for title in options)
print(
    "Streamlit AppTest passed: initial render, recap, conflicts, spoiler exclusion, approval, invalid cutoff, retry and transcript import."
)
# Import a live source, select it, append a later observation and recap that interval.
at.selectbox(key="import_kind").select("live")
at.text_input(key="import_title").set_value("Streamlit live test")
at.selectbox(key="import_format").select("json")
at.text_area(key="import_text").set_value(
    json.dumps(
        [
            {
                "id": "live-1",
                "start": 60,
                "end": 75,
                "text": "Synthetic runner at the start.",
                "kind": "commentary",
            }
        ]
    )
)
next(b for b in at.button if b.label == "Import source").click().run()
sources = at.session_state["api"].call("workspace")["sources"]
live = next(s for s in sources if s["title"] == "Streamlit live test")
at.selectbox(key="source_select").select(live["id"]).run()
at.checkbox(key="append_mode").check().run()
at.text_input(key="import_end").set_value("20:00")
at.text_area(key="import_text").set_value(
    json.dumps(
        [
            {
                "id": "live-2",
                "start": 960,
                "end": 975,
                "text": "Synthetic runner at the next checkpoint.",
                "kind": "timing",
            }
        ]
    )
)
next(b for b in at.button if b.label == "Append observations").click().run()
assert not at.exception, at.exception
assert any("revision 2" in item.value for item in at.success)
at.text_input(key="range_start").set_value("15:00")
at.text_input(key="range_end").set_value("20:00")
at.text_input(key="range_cutoff").set_value("20:00")
at.checkbox(key="simulate_failure").uncheck()
next(b for b in at.button if b.label == "Create recap").click().run()
assert [f["id"] for f in at.session_state["run"]["findings"]] == ["live-2"]
assert at.session_state["run"]["sourceRevision"] == 2
next(b for b in at.button if b.label == "Create recap").click().run()
assert at.session_state["run"]["cacheHit"]
assert any("Streamlit live test" in e.label for e in at.expander)
print(
    "Streamlit AppTest passed: live import, source selection, append, revision refresh, later-window recap, cache hit and current history."
)
