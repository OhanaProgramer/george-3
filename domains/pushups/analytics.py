"""Pushups analytics boundary.

Purpose: Calculate deterministic pushup progress and trend metrics.
Phase: Pushups Coach v1.
Last updated: 2026-06-03.
Notes: Structured data only; no LLM calls or UI rendering.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
import json
from statistics import median, pstdev
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from domains.pushups import service


GOAL_PERIOD_START = "2026-01-01"
ANALYTICS_FILE = service.DOMAIN_DIR / "data" / "analytics.json"


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _date_range(start: date, end: date) -> list[date]:
    if end < start:
        return []

    days = (end - start).days + 1
    return [start + timedelta(days=offset) for offset in range(days)]


def _round(value: float | None, digits: int = 2) -> float | None:
    if value is None:
        return None

    return round(value, digits)


def _event_local_datetime(event: dict) -> datetime:
    timestamp = str(event.get("ts") or "")
    timezone_name = str(event.get("tz") or "UTC")

    try:
        timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone = ZoneInfo("UTC")

    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return parsed.astimezone(timezone)


def _event_reps(event: dict) -> int:
    return int(event.get("reps") or 0)


def _utc_timestamp() -> str:
    return datetime.now(ZoneInfo("UTC")).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _window_average(daily_totals: dict[str, int], end: date, days: int) -> float:
    start = end - timedelta(days=days - 1)
    total = sum(daily_totals.get(day.isoformat(), 0) for day in _date_range(start, end))
    return total / days


def _rolling_average_on_day(
    daily_totals: dict[str, int],
    end: date,
    days: int,
) -> float:
    return _window_average(daily_totals, end, days)


def _active_days_in_window(daily_totals: dict[str, int], end: date, days: int) -> int:
    start = end - timedelta(days=days - 1)
    return sum(
        1
        for day in _date_range(start, end)
        if daily_totals.get(day.isoformat(), 0) > 0
    )


def _current_streak(daily_totals: dict[str, int], latest: date) -> int:
    streak = 0
    day = latest

    while daily_totals.get(day.isoformat(), 0) > 0:
        streak += 1
        day -= timedelta(days=1)

    return streak


def _longest_streak(daily_totals: dict[str, int], first: date, latest: date) -> int:
    longest = 0
    current = 0

    for day in _date_range(first, latest):
        if daily_totals.get(day.isoformat(), 0) > 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    return longest


def _weekly_jump(daily_totals: dict[str, int], latest: date) -> float | None:
    last_7_total = _window_average(daily_totals, latest, 7) * 7
    prior_7_end = latest - timedelta(days=7)
    prior_7_total = _window_average(daily_totals, prior_7_end, 7) * 7

    if prior_7_total <= 0:
        return None

    return ((last_7_total - prior_7_total) / prior_7_total) * 100


def _risk_label(weekly_jump_pct: float | None) -> str:
    if weekly_jump_pct is None:
        return "Unknown"

    absolute_jump = abs(weekly_jump_pct)
    if weekly_jump_pct < -20:
        return "Watch"
    if absolute_jump <= 10:
        return "Stable"
    if absolute_jump <= 20:
        return "Elevated"
    return "High"


def _events_by_local_day(events: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}

    for event in events:
        local_dt = _event_local_datetime(event)
        key = local_dt.date().isoformat()
        grouped.setdefault(key, []).append(event)

    return {key: sorted(value, key=_event_local_datetime) for key, value in sorted(grouped.items())}


def _latest_signal_day(events_by_day: dict[str, list[dict]], as_of_date: date | None = None) -> str:
    if not events_by_day:
        return ""

    if as_of_date is None:
        return max(events_by_day)

    possible_days = [day for day in events_by_day if _parse_date(day) <= as_of_date]
    return max(possible_days) if possible_days else max(events_by_day)


def _day_distribution_label(day_span_hours: float, sets_before_noon: int, sets_after_6pm: int, evening_reps_pct: float, latest_hour: int) -> str:
    if latest_hour >= 21 and day_span_hours <= 4 and evening_reps_pct >= 75:
        return "late-cram"

    if evening_reps_pct >= 60 or sets_after_6pm > sets_before_noon:
        return "evening-heavy"

    if day_span_hours >= 8 and sets_before_noon > 0 and sets_after_6pm > 0:
        return "spread-through-day"

    return "mixed"


def _build_day_distribution(events: list[dict], signal_day: str) -> dict:
    day_events = sorted(events, key=_event_local_datetime)

    if not day_events:
        return {
            "date": signal_day,
            "label": "mixed",
            "first_set_time": "",
            "last_set_time": "",
            "day_span_hours": 0,
            "sets_before_noon": 0,
            "sets_after_6pm": 0,
            "evening_reps_pct": 0,
            "latest_set_time": "",
        }

    local_times = [_event_local_datetime(event) for event in day_events]
    reps = [_event_reps(event) for event in day_events]
    total_reps = sum(reps)
    first = local_times[0]
    latest = local_times[-1]
    evening_reps = sum(_event_reps(event) for event in day_events if _event_local_datetime(event).hour >= 18)
    day_span_hours = (latest - first).total_seconds() / 3600 if len(local_times) > 1 else 0
    sets_before_noon = sum(1 for local_time in local_times if local_time.hour < 12)
    sets_after_6pm = sum(1 for local_time in local_times if local_time.hour >= 18)
    evening_reps_pct = (evening_reps / total_reps) * 100 if total_reps else 0

    return {
        "date": signal_day,
        "label": _day_distribution_label(day_span_hours, sets_before_noon, sets_after_6pm, evening_reps_pct, latest.hour),
        "first_set_time": first.strftime("%H:%M"),
        "last_set_time": latest.strftime("%H:%M"),
        "day_span_hours": _round(day_span_hours),
        "sets_before_noon": sets_before_noon,
        "sets_after_6pm": sets_after_6pm,
        "evening_reps_pct": _round(evening_reps_pct),
        "latest_set_time": latest.strftime("%H:%M"),
    }


def _events_in_day_window(events_by_day: dict[str, list[dict]], end_day: date, days: int) -> list[dict]:
    start_day = end_day - timedelta(days=days - 1)
    selected: list[dict] = []

    for day in _date_range(start_day, end_day):
        selected.extend(events_by_day.get(day.isoformat(), []))

    return selected


def _average_reps_per_set(events: list[dict]) -> float | None:
    if not events:
        return None

    return sum(_event_reps(event) for event in events) / len(events)


def _set_pattern_label(sets_per_day: int, avg_reps_per_set: float | None, avg_reps_per_set_7d: float | None, avg_reps_per_set_14d: float | None) -> str:
    if avg_reps_per_set_7d is None or avg_reps_per_set_14d is None:
        return "stable-set-size"

    if avg_reps_per_set_7d < avg_reps_per_set_14d - 2 and sets_per_day >= 3:
        return "smaller-sets-more-frequent"

    if avg_reps_per_set_7d > avg_reps_per_set_14d + 2 and sets_per_day <= 2:
        return "larger-sets-less-frequent"

    return "stable-set-size"


def _build_set_pattern(events_by_day: dict[str, list[dict]], signal_day: str) -> dict:
    signal_date = _parse_date(signal_day)
    day_events = events_by_day.get(signal_day, [])
    reps = [_event_reps(event) for event in day_events]
    window_7_events = _events_in_day_window(events_by_day, signal_date, 7)
    window_14_events = _events_in_day_window(events_by_day, signal_date, 14)
    avg_reps_per_set = _average_reps_per_set(day_events)
    avg_7 = _average_reps_per_set(window_7_events)
    avg_14 = _average_reps_per_set(window_14_events)

    return {
        "date": signal_day,
        "label": _set_pattern_label(len(day_events), avg_reps_per_set, avg_7, avg_14),
        "sets_per_day": len(day_events),
        "avg_reps_per_set": _round(avg_reps_per_set),
        "median_reps_per_set": _round(median(reps)) if reps else None,
        "largest_set": max(reps) if reps else 0,
        "smallest_set": min(reps) if reps else 0,
        "set_size_variability": _round(pstdev(reps)) if len(reps) > 1 else 0,
        "avg_reps_per_set_7d": _round(avg_7),
        "avg_reps_per_set_14d": _round(avg_14),
    }


def _entry_recency_label(hours_since_last_entry: float | None) -> str:
    if hours_since_last_entry is None:
        return "stale"

    if hours_since_last_entry <= 24:
        return "fresh"

    if hours_since_last_entry <= 72:
        return "aging"

    return "stale"


def _build_entry_recency(events: list[dict], now: datetime | None = None) -> dict:
    if not events:
        return {
            "label": "stale",
            "hours_since_last_entry": None,
            "latest_entry_timestamp": "",
        }

    now = now or datetime.now(ZoneInfo("UTC"))
    latest_event = max(events, key=_event_local_datetime)
    latest = datetime.fromisoformat(str(latest_event["ts"]).replace("Z", "+00:00"))
    hours_since_last_entry = (now.astimezone(ZoneInfo("UTC")) - latest.astimezone(ZoneInfo("UTC"))).total_seconds() / 3600

    return {
        "label": _entry_recency_label(hours_since_last_entry),
        "hours_since_last_entry": _round(max(0, hours_since_last_entry)),
        "latest_entry_timestamp": latest_event["ts"],
    }


def build_process_signals(events: list[dict], as_of_date: date | None = None, now: datetime | None = None) -> dict:
    """Return structured process observations from existing event data."""
    events_by_day = _events_by_local_day(events)
    signal_day = _latest_signal_day(events_by_day, as_of_date)

    if not signal_day:
        return {
            "day_distribution": {},
            "set_pattern": {},
            "entry_recency": _build_entry_recency([], now=now),
        }

    return {
        "day_distribution": _build_day_distribution(events_by_day.get(signal_day, []), signal_day),
        "set_pattern": _build_set_pattern(events_by_day, signal_day),
        "entry_recency": _build_entry_recency(events, now=now),
    }


def build_pushups_analytics(as_of: str | None = None) -> dict:
    """Return a structured Pushups Coach v1 analytics object."""
    events = service.load_events()
    goal = service.load_goal()
    daily_totals = service.group_events_by_local_day()

    if not events or not daily_totals:
        return {
            "success": False,
            "snapshot": {},
            "goal_progress": {},
            "trend": {},
            "process_signals": {},
            "risk": {"label": "Unknown"},
            "message": "",
            "error": "No pushup events found.",
        }

    first_event = service.get_first_event()
    latest_event = service.get_latest_event()
    first_date = min(daily_totals)
    latest_date = max(daily_totals)
    as_of_date = _parse_date(as_of or latest_date)
    target_date = _parse_date(goal["target_date"])
    start_date = _parse_date(goal.get("start_date", GOAL_PERIOD_START))
    period_start = _parse_date(GOAL_PERIOD_START)

    total_reps = service.total_reps()
    target_reps = int(goal["target_reps"])
    reps_remaining = max(0, target_reps - total_reps)
    days_remaining = max(0, (target_date - as_of_date).days + 1)
    required_per_day = reps_remaining / days_remaining if days_remaining else 0

    total_goal_days = (target_date - period_start).days + 1
    elapsed_goal_days = max(0, min(total_goal_days, (as_of_date - period_start).days + 1))
    expected_by_now = (target_reps * elapsed_goal_days) / total_goal_days
    ahead_behind = total_reps - expected_by_now

    avg_7 = _window_average(daily_totals, as_of_date, 7)
    avg_14 = _window_average(daily_totals, as_of_date, 14)
    avg_30 = _window_average(daily_totals, as_of_date, 30)
    avg_60 = _window_average(daily_totals, as_of_date, 60)
    weekly_jump_pct = _weekly_jump(daily_totals, as_of_date)
    projected_by_target = total_reps + (avg_30 * max(0, days_remaining - 1))

    coaching_window_days = max(0, (as_of_date - start_date).days + 1)
    calendar_days = max(0, (_parse_date(latest_date) - _parse_date(first_date)).days + 1)
    lifetime_avg_per_calendar_day = total_reps / calendar_days if calendar_days else 0

    return {
        "success": True,
        "as_of": as_of_date.isoformat(),
        "snapshot": {
            "first_entry_date": first_date,
            "latest_entry_date": latest_date,
            "first_event_timestamp": first_event["ts"] if first_event else "",
            "latest_event_timestamp": latest_event["ts"] if latest_event else "",
            "total_reps": total_reps,
            "total_events": len(events),
            "total_active_days": coaching_window_days,
            "total_calendar_days": calendar_days,
            "raw_training_days": sum(1 for reps in daily_totals.values() if reps > 0),
            "current_streak": _current_streak(daily_totals, as_of_date),
            "longest_streak": _longest_streak(daily_totals, _parse_date(first_date), as_of_date),
        },
        "goal_progress": {
            "goal_name": goal["goal_name"],
            "target_reps": target_reps,
            "target_date": goal["target_date"],
            "start_date": goal.get("start_date", GOAL_PERIOD_START),
            "reps_remaining": reps_remaining,
            "days_remaining": days_remaining,
            "required_per_day": _round(required_per_day),
            "expected_by_now": _round(expected_by_now),
            "ahead_behind": _round(ahead_behind),
            "on_track": ahead_behind >= 0,
            "projected_by_target_date": _round(projected_by_target),
        },
        "trend": {
            "average_7_day": _round(avg_7),
            "average_14_day": _round(avg_14),
            "average_30_day": _round(avg_30),
            "average_60_day": _round(avg_60),
            "life_time_average": _round(lifetime_avg_per_calendar_day),
            "weekly_jump_pct": _round(weekly_jump_pct),
            "active_days_last_30": _active_days_in_window(daily_totals, as_of_date, 30),
        },
        "risk": {
            "label": _risk_label(weekly_jump_pct),
            "weekly_jump_pct": _round(weekly_jump_pct),
        },
        "process_signals": build_process_signals(events, as_of_date=as_of_date),
        "message": "Pushups analytics calculated.",
        "error": "",
    }


def get_analytics(as_of: str | None = None) -> dict:
    """Compatibility-friendly public analytics entry point."""
    return build_pushups_analytics(as_of=as_of)


def get_analytics_path():
    """Return the derived current analytics state path."""
    return ANALYTICS_FILE


def build_analytics_json_state(generated_at: str | None = None) -> dict:
    """Return the derived current analytics state file object."""
    from domains.pushups import advisor

    result = get_analytics()
    events = service.load_events()
    latest_event = service.get_latest_event()
    assessment = advisor.build_assessment(result)

    return {
        "schema": 1,
        "domain": "pushups",
        "generated_at": generated_at or _utc_timestamp(),
        "source": {
            "events_file": service.get_events_path().name,
            "goal_file": service.get_goal_path().name,
            "event_count": len(events),
            "latest_event_ts": latest_event["ts"] if latest_event else "",
        },
        "latest": {
            "snapshot": result.get("snapshot", {}),
            "goal_progress": result.get("goal_progress", {}),
            "trend": result.get("trend", {}),
            "risk": result.get("risk", {}),
            "process_signals": result.get("process_signals", {}),
            "assessment": assessment,
        },
    }


def write_analytics_json(path=None) -> dict:
    """Atomically write the current derived analytics state file."""
    output_path = path or get_analytics_path()
    state = build_analytics_json_state()
    temp_path = output_path.with_suffix(f"{output_path.suffix}.tmp")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp_path.replace(output_path)

    return state


def get_chart_data(as_of: str | None = None) -> dict:
    """Return the proven 60-day chart data without presentation markup."""
    daily_totals = service.group_events_by_local_day()
    goal = service.load_goal()

    if not daily_totals:
        return {
            "daily_totals": [],
            "rolling_14d": [],
            "target": int(goal.get("chart_target", 0) or 0),
        }

    latest_date = _parse_date(as_of or max(daily_totals))
    start_date = latest_date - timedelta(days=59)
    days = _date_range(start_date, latest_date)

    daily_series = [
        {
            "date": day.isoformat(),
            "total": daily_totals.get(day.isoformat(), 0),
        }
        for day in days
    ]
    rolling_series = [
        {
            "date": day.isoformat(),
            "average": _round(_rolling_average_on_day(daily_totals, day, 14), 1),
        }
        for day in days
    ]

    return {
        "daily_totals": daily_series,
        "rolling_14d": rolling_series,
        "target": int(goal.get("chart_target", 0) or 0),
    }
