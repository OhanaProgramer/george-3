"""Pushups domain tests.

Purpose: Verify Pushups Coach v1 reads data, goal config, and analytics.
Phase: Pushups Coach v1.
Last updated: 2026-06-03.
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

    def test_events_file_contains_only_raw_pushup_set_events(self):
        for event in service.load_events():
            self.assertEqual(event["type"], "pushups.set")
            self.assertIsInstance(event["reps"], int)
            self.assertGreater(event["reps"], 0)
            self.assertTrue(event.get("ts"))
            self.assertTrue(event.get("tz"))
            self.assertTrue(event.get("source"))

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

    def test_process_signals_are_present(self):
        result = analytics.get_analytics()

        self.assertIn("process_signals", result)
        self.assertEqual(
            set(result["process_signals"].keys()),
            {"day_distribution", "set_pattern", "entry_recency"},
        )

    def test_process_signals_are_deterministic_from_fixture_events(self):
        events = [
            {"ts": "2026-06-01T13:00:00.000Z", "tz": "America/Chicago", "reps": 10},
            {"ts": "2026-06-01T23:30:00.000Z", "tz": "America/Chicago", "reps": 20},
            {"ts": "2026-06-02T01:30:00.000Z", "tz": "America/Chicago", "reps": 20},
        ]
        now = datetime.fromisoformat("2026-06-02T02:30:00+00:00")

        signals = analytics.build_process_signals(
            events,
            as_of_date=datetime.strptime("2026-06-01", "%Y-%m-%d").date(),
            now=now,
        )

        self.assertEqual(signals["day_distribution"]["label"], "evening-heavy")
        self.assertEqual(signals["day_distribution"]["first_set_time"], "08:00")
        self.assertEqual(signals["day_distribution"]["last_set_time"], "20:30")
        self.assertEqual(signals["day_distribution"]["sets_before_noon"], 1)
        self.assertEqual(signals["day_distribution"]["sets_after_6pm"], 2)
        self.assertEqual(signals["set_pattern"]["sets_per_day"], 3)
        self.assertEqual(signals["set_pattern"]["avg_reps_per_set"], 16.67)
        self.assertEqual(signals["set_pattern"]["median_reps_per_set"], 20)
        self.assertEqual(signals["set_pattern"]["largest_set"], 20)
        self.assertEqual(signals["set_pattern"]["smallest_set"], 10)
        self.assertEqual(signals["entry_recency"]["label"], "fresh")
        self.assertEqual(signals["entry_recency"]["hours_since_last_entry"], 1.0)

    def test_process_signal_labels_cover_late_cram_and_stale(self):
        events = [
            {"ts": "2026-06-01T02:00:00.000Z", "tz": "America/Chicago", "reps": 30},
            {"ts": "2026-06-01T03:00:00.000Z", "tz": "America/Chicago", "reps": 30},
        ]
        now = datetime.fromisoformat("2026-06-05T03:00:00+00:00")

        signals = analytics.build_process_signals(
            events,
            as_of_date=datetime.strptime("2026-05-31", "%Y-%m-%d").date(),
            now=now,
        )

        self.assertEqual(signals["day_distribution"]["label"], "late-cram")
        self.assertEqual(signals["entry_recency"]["label"], "stale")

    def test_analytics_json_state_contains_contract_fields(self):
        state = analytics.build_analytics_json_state(generated_at="2026-06-03T00:00:00.000Z")

        self.assertEqual(state["schema"], 1)
        self.assertEqual(state["domain"], "pushups")
        self.assertEqual(state["generated_at"], "2026-06-03T00:00:00.000Z")
        self.assertEqual(set(state["source"].keys()), {"events_file", "goal_file", "event_count", "latest_event_ts"})
        self.assertEqual(set(state["latest"].keys()), {"snapshot", "goal_progress", "trend", "risk", "process_signals", "assessment"})
        self.assertEqual(state["source"]["event_count"], service.count_events())
        self.assertIn("process_signals", state["latest"])

    def test_analytics_json_can_be_generated_to_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "analytics-test.json"

            state = analytics.write_analytics_json(path=output_path)
            saved = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(saved["schema"], 1)
        self.assertEqual(saved["domain"], "pushups")
        self.assertEqual(saved["source"]["event_count"], service.count_events())
        self.assertEqual(saved["source"]["latest_event_ts"], state["source"]["latest_event_ts"])
        self.assertIn("process_signals", saved["latest"])

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
