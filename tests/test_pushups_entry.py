"""Pushups Entry v1 tests."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from domains.pushups import service
from interfaces.web import pushups_app


def write_event(path: Path, timestamp: str, reps: int) -> dict:
    event = {
        "schema": 1,
        "id": f"test_{timestamp}",
        "ts": timestamp,
        "tz": "America/New_York",
        "type": "pushups.set",
        "reps": reps,
        "source": "test",
        "tags": [],
        "note": "",
    }
    with path.open("a", encoding="utf-8") as event_file:
        event_file.write(json.dumps(event) + "\n")
    return event


class PushupsEntryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.events_path = self.root / "events.ndjson"
        self.goal_path = self.root / "goal.json"
        write_event(self.events_path, "2026-06-01T12:00:00.000Z", 10)
        self.goal_path.write_text(
            json.dumps(
                {
                    "goal_name": "Test Goal",
                    "target_reps": 100,
                    "target_date": "2026-12-22",
                    "start_date": "2026-06-01",
                }
            ),
            encoding="utf-8",
        )
        self.events_patch = patch.object(service, "EVENTS_FILE", self.events_path)
        self.goal_patch = patch.object(service, "GOAL_FILE", self.goal_path)
        self.events_patch.start()
        self.goal_patch.start()

    def tearDown(self):
        self.goal_patch.stop()
        self.events_patch.stop()
        self.temp_dir.cleanup()

    def test_valid_entry_appends(self):
        event = service.add_event(
            12,
            timestamp="2026-06-01T13:00:00.000Z",
            source="web",
        )

        self.assertEqual(event["reps"], 12)
        self.assertEqual(service.count_events(), 2)
        self.assertTrue((self.root / "backups").exists())

    def test_invalid_entry_rejected(self):
        with self.assertRaises(ValueError):
            service.add_event(0, timestamp="2026-06-01T13:00:00.000Z")

        self.assertEqual(service.count_events(), 1)

    def test_today_total_updates(self):
        service.add_event(5, timestamp="2026-06-01T13:00:00.000Z")

        self.assertEqual(service.get_today_total("2026-06-01"), 15)

    def test_latest_event_updates(self):
        service.add_event(7, timestamp="2026-06-01T13:00:00.000Z")

        latest = service.get_latest_event()
        self.assertEqual(latest["reps"], 7)
        self.assertEqual(latest["source"], "web")

    def test_form_validation_rejects_bad_reps(self):
        success, message = pushups_app.save_pushups_form({"reps": "-3"})

        self.assertFalse(success)
        self.assertIn("positive integer", message)
        self.assertEqual(service.count_events(), 1)

    def test_pushups_page_includes_proven_chart(self):
        html = pushups_app.render_pushups_page()

        self.assertIn("Last 60 days (bars) + 14-day average (line)", html)
        self.assertIn("Current 14-day average is", html)
        self.assertIn("Target:", html)
        self.assertIn("Current 14d avg:", html)
        self.assertIn("George Assessment", html)

    def test_report_still_runs(self):
        completed = subprocess.run(
            [sys.executable, "-m", "domains.pushups.report"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Pushups Coach v1", completed.stdout)
        self.assertIn("Result: SUCCESS", completed.stdout)


if __name__ == "__main__":
    unittest.main()
