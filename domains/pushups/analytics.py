"""Pushups analytics boundary.

Purpose: Calculate deterministic pushup progress and trend metrics.
Phase: Pushups Coach v1.
Last updated: 2026-06-01.
Notes: Structured data only; no LLM calls or UI rendering.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from domains.pushups import service


GOAL_PERIOD_START = "2026-01-01"


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


def _window_average(daily_totals: dict[str, int], end: date, days: int) -> float:
    start = end - timedelta(days=days - 1)
    total = sum(daily_totals.get(day.isoformat(), 0) for day in _date_range(start, end))
    return total / days


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
        "message": "Pushups analytics calculated.",
        "error": "",
    }


def get_analytics(as_of: str | None = None) -> dict:
    """Compatibility-friendly public analytics entry point."""
    return build_pushups_analytics(as_of=as_of)
