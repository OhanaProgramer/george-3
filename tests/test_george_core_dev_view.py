"""George Core dev view tests.

Purpose: Verify Core reads domain analytics and applies simple thresholds.
Phase: George Core Dev View v1.
Last updated: 2026-06-03.
Notes: Read-only tests for derived analytics contracts.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from core.george_core import dev_view, domain_reader, evaluator


CONSIDERED_AT = "2026-06-03T12:00:00.000Z"


def sample_analytics(entry_recency: str = "fresh", risk: str = "Stable", on_track: bool = True) -> dict:
    return {
        "schema": 1,
        "domain": "pushups",
        "generated_at": "2026-06-03T11:00:00.000Z",
        "source": {"events_file": "events.ndjson", "goal_file": "goal.json", "event_count": 1, "latest_event_ts": "2026-06-03T10:00:00.000Z"},
        "latest": {
            "snapshot": {},
            "goal_progress": {},
            "trend": {},
            "risk": {"label": risk},
            "process_signals": {
                "entry_recency": {"label": entry_recency},
                "day_distribution": {"label": "mixed"},
                "set_pattern": {"label": "stable-set-size"},
            },
            "assessment": {"on_track": on_track},
        },
    }


class GeorgeCoreDevViewTests(unittest.TestCase):
    def test_reader_loads_pushups_analytics_json(self):
        states = domain_reader.load_domain_states()
        pushups = [state for state in states if state["domain"] == "pushups"]

        self.assertEqual(len(pushups), 1)
        self.assertEqual(pushups[0]["load_status"], "loaded")
        self.assertEqual(pushups[0]["data"]["domain"], "pushups")

    def test_evaluator_returns_none_for_normal_pushups_state(self):
        state = {"domain": "pushups", "load_status": "loaded", "data": sample_analytics()}

        result = evaluator.evaluate_domain_state(state, considered_at=CONSIDERED_AT)

        self.assertEqual(result["core_response"], "none")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["reason"], "No significant signal.")

    def test_evaluator_returns_observe_for_aging_entry_recency(self):
        state = {"domain": "pushups", "load_status": "loaded", "data": sample_analytics(entry_recency="aging")}

        result = evaluator.evaluate_domain_state(state, considered_at=CONSIDERED_AT)

        self.assertEqual(result["core_response"], "observe")
        self.assertEqual(result["status"], "aging")
        self.assertEqual(result["reason"], "Domain entry recency is aging.")

    def test_evaluator_returns_report_for_stale_entry_recency(self):
        state = {"domain": "pushups", "load_status": "loaded", "data": sample_analytics(entry_recency="stale")}

        result = evaluator.evaluate_domain_state(state, considered_at=CONSIDERED_AT)

        self.assertEqual(result["core_response"], "report")
        self.assertEqual(result["status"], "stale")
        self.assertEqual(result["reason"], "Domain reports stale entry recency.")

    def test_evaluator_returns_report_for_missing_analytics(self):
        state = {"domain": "pushups", "load_status": "missing", "data": {}, "error": "analytics.json not found"}

        result = evaluator.evaluate_domain_state(state, considered_at=CONSIDERED_AT)

        self.assertEqual(result["core_response"], "report")
        self.assertEqual(result["status"], "missing")
        self.assertEqual(result["reason"], "Domain analytics.json is missing.")

    def test_reader_handles_malformed_analytics_json(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            domain_dir = Path(tmp_dir) / "domains" / "bad"
            data_dir = domain_dir / "data"
            data_dir.mkdir(parents=True)
            (data_dir / "analytics.json").write_text("{bad json", encoding="utf-8")

            states = domain_reader.load_domain_states(project_root=Path(tmp_dir))

        self.assertEqual(states[0]["domain"], "bad")
        self.assertEqual(states[0]["load_status"], "malformed")

    def test_dev_cli_runs(self):
        completed = subprocess.run(
            [sys.executable, "-m", "core.george_core.dev_view"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("George Core Dev View", completed.stdout)
        self.assertIn("Domain: pushups", completed.stdout)
        self.assertIn("Result: SUCCESS", completed.stdout)


if __name__ == "__main__":
    unittest.main()
