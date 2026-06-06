"""Pushups Coach v1 report command.

Purpose: Render deterministic pushup analytics as plain text.
Phase: Pushups Coach v1.
Last updated: 2026-06-03.
Notes: Display only; structured analytics remain the domain product.
"""

from __future__ import annotations

from domains.pushups import advisor, analytics


def build_report() -> str:
    """Return the plain text Pushups Coach v1 report."""
    analytics.write_analytics_json()
    result = analytics.get_analytics()
    assessment = advisor.build_assessment(result)

    if not result.get("success"):
        return "\n".join(
            [
                "Pushups Coach v1",
                "",
                "Result: ERROR",
                f"Error: {result.get('error', 'Unknown error')}",
            ]
        )

    snapshot = result["snapshot"]
    goal = result["goal_progress"]
    trend = result["trend"]
    signals = result["process_signals"]
    day_distribution = signals["day_distribution"]
    set_pattern = signals["set_pattern"]
    entry_recency = signals["entry_recency"]

    return "\n".join(
        [
            "Pushups Coach v1",
            "",
            "Snapshot",
            f"First Entry: {snapshot['first_entry_date']}",
            f"Latest Entry: {snapshot['latest_entry_date']}",
            f"Total Reps: {snapshot['total_reps']}",
            f"Events: {snapshot['total_events']}",
            f"Active Days: {snapshot['total_active_days']}",
            f"Calendar Days: {snapshot['total_calendar_days']}",
            f"Current Streak: {snapshot['current_streak']}",
            f"Longest Streak: {snapshot['longest_streak']}",
            "",
            "Goal Progress",
            f"Goal: {goal['goal_name']}",
            f"Target: {goal['target_reps']} by {goal['target_date']}",
            f"Remaining: {goal['reps_remaining']}",
            f"Days Remaining: {goal['days_remaining']}",
            f"Required Per Day: {goal['required_per_day']}",
            f"Ahead / Behind: {goal['ahead_behind']}",
            f"Projected By Target: {goal['projected_by_target_date']}",
            "",
            "Trend",
            f"7-Day Average: {trend['average_7_day']}",
            f"14-Day Average: {trend['average_14_day']}",
            f"30-Day Average: {trend['average_30_day']}",
            f"60-Day Average: {trend['average_60_day']}",
            f"Lifetime Daily Average: {trend['life_time_average']}",
            f"Weekly Jump: {trend['weekly_jump_pct']}%",
            f"Active Days Last 30: {trend['active_days_last_30']}",
            "",
            "Process Signals",
            f"Day Distribution: {day_distribution['label']}",
            f"Set Pattern: {set_pattern['label']}",
            f"Entry Recency: {entry_recency['label']}",
            "",
            "George Assessment",
            f"Status: {assessment['status']}",
            f"Where: {assessment['where_am_i']}",
            f"Reason: {assessment['reason']}",
            f"Risk: {assessment['risk_label']}",
            f"Note: {assessment['note']}",
            f"Next 7 Days: {assessment['next_7_days']}",
            "",
            "Result: SUCCESS",
        ]
    )


def main() -> None:
    print(build_report())


if __name__ == "__main__":
    main()
