"""Pushups domain tests.

Purpose: Verify Pushups Coach v1 reads data, goal config, and analytics.
Phase: Pushups Coach v1.
Last updated: 2026-06-01.
Notes: Read-only tests; no data mutation or app wiring.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from domains.pushups import advisor, analytics, service


MIN_EXPECTED_LATEST_TS = "2026-06-01T15:20:29.964Z"
MIN_EXPECTED_LATEST_DATE = "2026-06-01"


def parse_utc_timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


class PushupsDomainTests(unittest.TestCase):
    def run_with_fixture(self, events, goal, callback):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            events_path = temp_path / "events.ndjson"
            goal_path = temp_path / "goal.json"

            with events_path.open("w", encoding="utf-8") as event_file:
                for event in events:
                    event_file.write(json.dumps(event, separators=(",", ":")) + "\n")

            with goal_path.open("w", encoding="utf-8") as goal_file:
                json.dump(goal, goal_file)

            original_events_file = service.EVENTS_FILE
            original_goal_file = service.GOAL_FILE
            try:
                service.EVENTS_FILE = events_path
                service.GOAL_FILE = goal_path
                callback()
            finally:
                service.EVENTS_FILE = original_events_file
                service.GOAL_FILE = original_goal_file

    def fixed_events(self):
        return [
            {
                "schema": 1,
                "id": "evt_fixture_1",
                "ts": "2026-01-01T12:00:00.000Z",
                "tz": "UTC",
                "type": "pushups.set",
                "reps": 10,
                "source": "test",
                "tags": [],
                "note": "",
            },
            {
                "schema": 1,
                "id": "evt_fixture_2",
                "ts": "2026-01-03T12:00:00.000Z",
                "tz": "UTC",
                "type": "pushups.set",
                "reps": 20,
                "source": "test",
                "tags": [],
                "note": "",
            },
            {
                "schema": 1,
                "id": "evt_fixture_3",
                "ts": "2026-01-03T18:00:00.000Z",
                "tz": "UTC",
                "type": "pushups.set",
                "reps": 5,
                "source": "test",
                "tags": [],
                "note": "",
            },
        ]

    def fixed_goal(self):
        return {
            "goal_name": "Fixture Goal",
            "target_reps": 100,
            "target_date": "2026-01-10",
            "start_date": "2026-01-01",
            "timezone": "UTC",
            "chart_target": 12,
        }

    def test_events_file_exists(self):
        self.assertTrue(service.get_events_path().exists())

    def test_load_events_returns_records(self):
        events = service.load_events()

        self.assertGreater(len(events), 0)
        self.assertEqual(events[0]["type"], "pushups.set")

    def test_count_events_is_positive(self):
        self.assertGreater(service.count_events(), 0)

    def test_latest_event_is_not_older_than_promoted_source(self):
        latest = service.get_latest_event()

        self.assertIsNotNone(latest)
        self.assertGreaterEqual(
            parse_utc_timestamp(latest["ts"]),
            parse_utc_timestamp(MIN_EXPECTED_LATEST_TS),
        )

    def test_goal_loads_from_goal_json(self):
        goal = service.load_goal()

        self.assertEqual(goal["goal_name"], "Birthday Pushups 2026")
        self.assertEqual(goal["target_reps"], 30000)
        self.assertEqual(goal["target_date"], "2026-12-22")
        self.assertEqual(goal["timezone"], "America/Chicago")
        self.assertEqual(goal["chart_target"], 130)

    def test_total_reps_matches_authoritative_dataset(self):
        expected_total = sum(event["reps"] for event in service.load_events())

        self.assertEqual(service.total_reps(), expected_total)
        self.assertGreater(service.total_reps(), 0)

    def test_pushups_live_analytics_snapshot_is_sane(self):
        result = analytics.get_analytics()
        expected_total = service.total_reps()

        self.assertTrue(result["success"])
        self.assertEqual(result["snapshot"]["total_reps"], expected_total)
        self.assertGreater(result["snapshot"]["total_events"], 0)
        self.assertGreater(result["snapshot"]["total_active_days"], 0)
        self.assertGreater(result["snapshot"]["total_calendar_days"], 0)
        self.assertGreaterEqual(
            result["snapshot"]["latest_entry_date"],
            MIN_EXPECTED_LATEST_DATE,
        )

    def test_fixture_lifetime_average_uses_calendar_days(self):
        def assert_fixture():
            result = analytics.get_analytics(as_of="2026-01-05")

            self.assertEqual(result["snapshot"]["total_reps"], 35)
            self.assertEqual(result["snapshot"]["total_events"], 3)
            self.assertEqual(result["snapshot"]["latest_entry_date"], "2026-01-03")
            self.assertEqual(result["snapshot"]["total_calendar_days"], 3)
            self.assertEqual(result["trend"]["life_time_average"], 11.67)

        self.run_with_fixture(self.fixed_events(), self.fixed_goal(), assert_fixture)

    def test_fixture_required_per_day_calculation(self):
        def assert_fixture():
            result = analytics.get_analytics(as_of="2026-01-05")

            self.assertEqual(result["goal_progress"]["reps_remaining"], 65)
            self.assertEqual(result["goal_progress"]["days_remaining"], 6)
            self.assertEqual(result["goal_progress"]["required_per_day"], 10.83)

        self.run_with_fixture(self.fixed_events(), self.fixed_goal(), assert_fixture)

    def test_live_goal_progress_is_sane(self):
        result = analytics.get_analytics()
        goal_progress = result["goal_progress"]

        self.assertGreaterEqual(goal_progress["reps_remaining"], 0)
        self.assertGreaterEqual(goal_progress["days_remaining"], 0)
        self.assertGreater(goal_progress["required_per_day"], 0)

    def test_window_analytics_are_present(self):
        result = analytics.get_analytics()
        trend = result["trend"]

        self.assertIn("average_7_day", trend)
        self.assertIn("average_14_day", trend)
        self.assertIn("average_30_day", trend)
        self.assertIn("average_60_day", trend)

    def test_chart_data_returns_proven_chart_shape(self):
        chart = analytics.get_chart_data()

        self.assertEqual(set(chart.keys()), {"daily_totals", "rolling_14d", "target"})
        self.assertLessEqual(len(chart["daily_totals"]), 60)
        self.assertLessEqual(len(chart["rolling_14d"]), 60)
        self.assertEqual(len(chart["daily_totals"]), len(chart["rolling_14d"]))
        self.assertEqual(chart["target"], 130)
        self.assertGreaterEqual(chart["daily_totals"][-1]["date"], MIN_EXPECTED_LATEST_DATE)
        self.assertIn("total", chart["daily_totals"][-1])
        self.assertIn("average", chart["rolling_14d"][-1])

    def test_fixture_chart_data_returns_exact_series(self):
        def assert_fixture():
            chart = analytics.get_chart_data(as_of="2026-01-05")

            self.assertEqual(len(chart["daily_totals"]), 60)
            self.assertEqual(len(chart["rolling_14d"]), 60)
            self.assertEqual(chart["target"], 12)
            self.assertEqual(chart["daily_totals"][-5:], [
                {"date": "2026-01-01", "total": 10},
                {"date": "2026-01-02", "total": 0},
                {"date": "2026-01-03", "total": 25},
                {"date": "2026-01-04", "total": 0},
                {"date": "2026-01-05", "total": 0},
            ])
            self.assertEqual(chart["rolling_14d"][-1]["average"], 2.5)

        self.run_with_fixture(self.fixed_events(), self.fixed_goal(), assert_fixture)

    def test_advisor_returns_required_fields(self):
        assessment = advisor.get_assessment()

        self.assertIn("status", assessment)
        self.assertIn("reason", assessment)
        self.assertIn("next_7_days", assessment)

    def test_report_command_runs(self):
        completed = subprocess.run(
            [sys.executable, "-m", "domains.pushups.report"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Pushups Coach v1", completed.stdout)
        self.assertIn("George Assessment", completed.stdout)
        self.assertIn("Result: SUCCESS", completed.stdout)


if __name__ == "__main__":
    unittest.main()
