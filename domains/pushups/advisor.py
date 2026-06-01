"""Pushups advisor boundary.

Purpose: Create deterministic George commentary for pushup goals.
Phase: Pushups Coach v1.
Last updated: 2026-06-01.
Notes: Rule-based only; no LLM calls.
"""

from __future__ import annotations

from domains.pushups import analytics


def build_assessment(analytics_result: dict | None = None) -> dict:
    """Return George-style pushup guidance from structured analytics."""
    result = analytics_result or analytics.get_analytics()
    if not result.get("success"):
        return {
            "status": "Error",
            "reason": result.get("error", "Pushups analytics unavailable."),
            "risk_label": "Unknown",
            "note": "George cannot assess pushup progress without readable data.",
            "next_7_days": "Restore the dataset, then rerun Pushups Coach.",
        }

    snapshot = result["snapshot"]
    goal = result["goal_progress"]
    trend = result["trend"]
    risk = result["risk"]

    status = "On track" if goal["on_track"] else "Behind"
    if goal["on_track"] and goal["ahead_behind"] > 500:
        status = "Ahead"

    required = goal["required_per_day"]
    avg_7 = trend["average_7_day"]
    avg_30 = trend["average_30_day"]

    if goal["on_track"]:
        reason = (
            f"You have {snapshot['total_reps']} reps against "
            f"{goal['target_reps']}, {goal['ahead_behind']} reps ahead of pace."
        )
    else:
        reason = (
            f"You have {snapshot['total_reps']} reps against "
            f"{goal['target_reps']}, {abs(goal['ahead_behind'])} reps behind pace."
        )

    if risk["label"] == "High":
        note = "Volume changed sharply this week. Protect the habit and recovery."
    elif risk["label"] == "Watch":
        note = "Recent volume dropped meaningfully. Rebuild with controlled daily reps."
    elif avg_7 >= avg_30:
        note = "Recent work is at or above your 30-day baseline. Keep the rhythm boring and reliable."
    else:
        note = "Recent work is below your 30-day baseline. Tighten the next week."

    next_7_days = (
        f"Average at least {round(required)} reps per day for the next 7 days. "
        "Use smaller sets if needed; the win is showing up."
    )

    return {
        "status": status,
        "where_am_i": (
            f"{snapshot['total_reps']} reps logged over "
            f"{snapshot['total_active_days']} coaching days."
        ),
        "on_track": goal["on_track"],
        "reason": reason,
        "risk_label": risk["label"],
        "note": note,
        "next_7_days": next_7_days,
    }


def get_assessment() -> dict:
    """Public advisor entry point."""
    return build_assessment()
