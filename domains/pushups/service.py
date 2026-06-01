"""Pushups data access boundary.

Purpose: Read the active pushup raw event dataset and goal config.
Phase: Pushups Coach v1.
Last updated: 2026-06-01.
Notes: Read-only helpers only; no writes or runtime wiring.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DOMAIN_DIR = Path(__file__).resolve().parent
EVENTS_FILE = DOMAIN_DIR / "data" / "events.ndjson"
GOAL_FILE = DOMAIN_DIR / "data" / "goal.json"


def get_events_path() -> Path:
    """Return the active local raw pushup event dataset path."""
    return EVENTS_FILE


def get_goal_path() -> Path:
    """Return the active local pushup goal config path."""
    return GOAL_FILE


def load_events() -> list[dict]:
    """Load active pushup events from NDJSON without mutating the file."""
    events = []

    with get_events_path().open("r", encoding="utf-8") as event_file:
        for line in event_file:
            if line.strip():
                events.append(json.loads(line))

    return events


def load_goal() -> dict:
    """Load the active pushup goal config without mutating the file."""
    with get_goal_path().open("r", encoding="utf-8") as goal_file:
        return json.load(goal_file)


def get_latest_event() -> dict | None:
    """Return the latest event by file order, or None when the dataset is empty."""
    latest = None

    with get_events_path().open("r", encoding="utf-8") as event_file:
        for line in event_file:
            if line.strip():
                latest = json.loads(line)

    return latest


def get_first_event() -> dict | None:
    """Return the first event by file order, or None when the dataset is empty."""
    with get_events_path().open("r", encoding="utf-8") as event_file:
        for line in event_file:
            if line.strip():
                return json.loads(line)

    return None


def count_events() -> int:
    """Count active pushup event records without loading derived analytics."""
    with get_events_path().open("r", encoding="utf-8") as event_file:
        return sum(1 for line in event_file if line.strip())


def total_reps() -> int:
    """Return total reps in the active raw event dataset."""
    return sum(int(event.get("reps") or 0) for event in load_events())


def _event_local_date(event: dict) -> str:
    timestamp = str(event.get("ts") or "")
    timezone_name = str(event.get("tz") or "UTC")

    try:
        timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone = ZoneInfo("UTC")

    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return parsed.astimezone(timezone).date().isoformat()


def group_events_by_local_day() -> dict[str, int]:
    """Return pushup totals keyed by each event's configured local day."""
    daily_totals: dict[str, int] = defaultdict(int)

    for event in load_events():
        daily_totals[_event_local_date(event)] += int(event.get("reps") or 0)

    return dict(sorted(daily_totals.items()))
