"""Pushups domain tests.

Purpose: Verify Pushups Coach v1 reads data, goal config, and analytics.
Phase: Pushups Coach v1.
Last updated: 2026-06-01.
Notes: Read-only tests; no data mutation or app wiring.
"""

from datetime import datetime, timezone
import subprocess
import sys
import unittest

from domains.pushups import advisor, analytics, service


MIN_EXPECTED_LATEST_TS = "2026-06-01T15:20:29.964Z"


def parse_utc_timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


class PushupsDomainTests(unittest.TestCase):
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

    def test_total_reps_matches_authoritative_dataset(self):
        self.assertEqual(service.total_reps(), 13497)

    def test_pushups_analytics_snapshot_matches_expected_dataset(self):
        result = analytics.get_analytics()

        self.assertTrue(result["success"])
        self.assertEqual(result["snapshot"]["total_reps"], 13497)
        self.assertEqual(result["snapshot"]["total_active_days"], 66)
        self.assertEqual(result["snapshot"]["latest_entry_date"], "2026-06-01")

    def test_life_time_average_uses_calendar_days(self):
        result = analytics.get_analytics()

        self.assertEqual(result["trend"]["life_time_average"], round(13497 / 152, 2))

    def test_required_per_day_calculation(self):
        result = analytics.get_analytics()

        self.assertEqual(result["goal_progress"]["reps_remaining"], 16503)
        self.assertEqual(result["goal_progress"]["days_remaining"], 205)
        self.assertEqual(result["goal_progress"]["required_per_day"], 80.5)

    def test_window_analytics_are_present(self):
        result = analytics.get_analytics()
        trend = result["trend"]

        self.assertIn("average_7_day", trend)
        self.assertIn("average_14_day", trend)
        self.assertIn("average_30_day", trend)
        self.assertIn("average_60_day", trend)

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
