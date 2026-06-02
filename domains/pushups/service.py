"""Pushups data access boundary.

Purpose: Read and append pushup events plus goal config.
Phase: Pushup Entry v1.
Last updated: 2026-06-01.
Notes: Writes are append-only NDJSON with pre-entry backup protection.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DOMAIN_DIR = Path(__file__).resolve().parent
EVENTS_FILE = DOMAIN_DIR / "data" / "events.ndjson"
GOAL_FILE = DOMAIN_DIR / "data" / "goal.json"
BACKUPS_DIR = DOMAIN_DIR / "data" / "backups"


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


def _coerce_positive_reps(reps) -> int:
    try:
        reps_value = int(reps)
    except (TypeError, ValueError) as error:
        raise ValueError("reps must be a positive integer") from error

    if reps_value <= 0:
        raise ValueError("reps must be a positive integer")

    return reps_value


def _format_timestamp(timestamp=None) -> str:
    if timestamp is None:
        now = datetime.now(timezone.utc)
    elif isinstance(timestamp, datetime):
        now = timestamp.astimezone(timezone.utc)
    elif isinstance(timestamp, str):
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        now = parsed.astimezone(timezone.utc)
    else:
        raise ValueError("timestamp must be a datetime, ISO timestamp, or None")

    return now.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _infer_event_timezone() -> str:
    try:
        goal = load_goal()
    except FileNotFoundError:
        goal = {}

    if goal.get("timezone"):
        return str(goal["timezone"])

    latest = get_latest_event()
    if latest and latest.get("tz"):
        return str(latest["tz"])

    return "UTC"


def _event_id(timestamp: str) -> str:
    compact = timestamp.replace("-", "").replace(":", "").replace(".", "")
    return f"evt_{compact}_{time.time_ns()}"


def _backup_root() -> Path:
    return get_events_path().parent / "backups"


def ensure_pre_entry_backup() -> Path:
    """Create the pre-entry backup once before the first append."""
    backups_root = _backup_root()
    existing = sorted(backups_root.glob("pre_entry_v1_*/events.ndjson"))
    if existing:
        return existing[-1].parent

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    backup_dir = backups_root / f"pre_entry_v1_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    shutil.copy2(get_events_path(), backup_dir / "events.ndjson")
    return backup_dir


def add_event(reps, timestamp=None, source: str = "web") -> dict:
    """Append one pushup event to the active NDJSON dataset."""
    reps_value = _coerce_positive_reps(reps)
    event_timestamp = _format_timestamp(timestamp)
    event = {
        "schema": 1,
        "id": _event_id(event_timestamp),
        "ts": event_timestamp,
        "tz": _infer_event_timezone(),
        "type": "pushups.set",
        "reps": reps_value,
        "source": str(source or "web"),
        "tags": [],
        "note": "",
    }

    ensure_pre_entry_backup()

    with get_events_path().open("a", encoding="utf-8") as event_file:
        event_file.write(json.dumps(event, separators=(",", ":")) + "\n")

    return event


def get_today_total(today: str | None = None) -> int:
    """Return the pushup total for today using the dataset's local date keys."""
    daily_totals = group_events_by_local_day()
    if today is None:
        today = _event_local_date({"ts": _format_timestamp(), "tz": _infer_event_timezone()})

    return daily_totals.get(today, 0)
