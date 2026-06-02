"""Pushup timezone and coaching-day behavior tests."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from domains.pushups import analytics, service


class PushupsTimezoneTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.events_path = self.root / "events.ndjson"
        self.goal_path = self.root / "goal.json"
        self.events_path.write_text("", encoding="utf-8")
        self.goal_path.write_text(
            json.dumps(
                {
                    "goal_name": "Timezone Test",
                    "target_reps": 30000,
                    "target_date": "2026-12-22",
                    "start_date": "2026-06-01",
                    "timezone": "America/Chicago",
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

    def test_morning_central_counts_to_same_local_day(self):
        event = service.add_event(
            33,
            timestamp="2026-06-01T10:00:00-05:00",
            source="test",
        )

        self.assertEqual(event["ts"], "2026-06-01T15:00:00.000Z")
        self.assertEqual(event["tz"], "America/Chicago")
        self.assertEqual(service.group_events_by_local_day(), {"2026-06-01": 33})

    def test_late_night_central_counts_to_same_local_day(self):
        event = service.add_event(
            33,
            timestamp="2026-06-01T23:59:00-05:00",
            source="test",
        )

        self.assertEqual(event["ts"], "2026-06-02T04:59:00.000Z")
        self.assertEqual(event["tz"], "America/Chicago")
        self.assertEqual(service.group_events_by_local_day(), {"2026-06-01": 33})

    def test_utc_late_night_equivalent_keeps_central_coaching_day(self):
        event = service.add_event(
            33,
            timestamp="2026-06-02T04:59:00Z",
            source="test",
        )

        self.assertEqual(event["ts"], "2026-06-02T04:59:00.000Z")
        self.assertEqual(event["tz"], "America/Chicago")
        self.assertEqual(service.group_events_by_local_day(), {"2026-06-01": 33})

    def test_analytics_windows_group_by_local_coaching_day(self):
        service.add_event(10, timestamp="2026-06-01T10:00:00-05:00", source="test")
        service.add_event(20, timestamp="2026-06-01T23:59:00-05:00", source="test")
        service.add_event(30, timestamp="2026-06-02T10:00:00-05:00", source="test")

        result = analytics.get_analytics(as_of="2026-06-02")

        self.assertEqual(service.group_events_by_local_day()["2026-06-01"], 30)
        self.assertEqual(result["snapshot"]["latest_entry_date"], "2026-06-02")
        self.assertEqual(result["snapshot"]["current_streak"], 2)
        self.assertEqual(result["trend"]["active_days_last_30"], 2)
        self.assertEqual(result["trend"]["average_7_day"], round(60 / 7, 2))
        self.assertEqual(result["trend"]["average_14_day"], round(60 / 14, 2))
        self.assertEqual(result["trend"]["average_30_day"], round(60 / 30, 2))
        self.assertEqual(result["trend"]["average_60_day"], round(60 / 60, 2))


if __name__ == "__main__":
    unittest.main()
