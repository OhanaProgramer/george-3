"""George Core threshold evaluator.

Purpose: Decide whether domain analytics rise above a reporting threshold.
Phase: George Core Dev View v1.
Last updated: 2026-06-03.
Notes: Reads domain output only; no domain recalculation or action execution.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_timestamp() -> str:
    """Return a compact UTC timestamp for Core consideration time."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _signal_value(data: dict[str, Any], *keys: str) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _signals_reviewed(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "risk": _signal_value(data, "latest", "risk", "label"),
        "entry_recency": _signal_value(data, "latest", "process_signals", "entry_recency", "label"),
        "day_distribution": _signal_value(data, "latest", "process_signals", "day_distribution", "label"),
        "set_pattern": _signal_value(data, "latest", "process_signals", "set_pattern", "label"),
        "on_track": _signal_value(data, "latest", "assessment", "on_track"),
    }


def evaluate_domain_state(domain_state: dict[str, Any], considered_at: str | None = None) -> dict[str, Any]:
    """Return a Core Evaluation object for one domain state."""
    last_considered_at = considered_at or utc_timestamp()
    domain = str(domain_state.get("domain") or "unknown")
    load_status = domain_state.get("load_status")

    base = {
        "domain": domain,
        "generated_at": "",
        "last_considered_at": last_considered_at,
        "status": "ok",
        "core_response": "none",
        "reason": "No significant signal.",
        "signals_reviewed": {},
        "significant_signals": [],
    }

    if load_status == "missing":
        return {
            **base,
            "status": "missing",
            "core_response": "report",
            "reason": "Domain analytics.json is missing.",
            "significant_signals": ["analytics_json_missing"],
        }

    if load_status == "malformed":
        return {
            **base,
            "status": "malformed",
            "core_response": "report",
            "reason": "Domain analytics.json is malformed.",
            "significant_signals": ["analytics_json_malformed"],
        }

    data = domain_state.get("data") if isinstance(domain_state.get("data"), dict) else {}
    reviewed = _signals_reviewed(data)
    base["generated_at"] = str(data.get("generated_at") or "")
    base["signals_reviewed"] = reviewed

    if reviewed["on_track"] is False:
        return {
            **base,
            "status": "off_track",
            "core_response": "report",
            "reason": "Domain reports off-track.",
            "significant_signals": ["assessment.on_track=false"],
        }

    if reviewed["risk"] == "High":
        return {
            **base,
            "status": "high_risk",
            "core_response": "report",
            "reason": "Domain reports high risk.",
            "significant_signals": ["risk.label=High"],
        }

    if reviewed["entry_recency"] == "stale":
        return {
            **base,
            "status": "stale",
            "core_response": "report",
            "reason": "Domain reports stale entry recency.",
            "significant_signals": ["process_signals.entry_recency.label=stale"],
        }

    if reviewed["entry_recency"] == "aging":
        return {
            **base,
            "status": "aging",
            "core_response": "observe",
            "reason": "Domain entry recency is aging.",
            "significant_signals": ["process_signals.entry_recency.label=aging"],
        }

    return base


def evaluate_domain_states(domain_states: list[dict[str, Any]], considered_at: str | None = None) -> list[dict[str, Any]]:
    """Evaluate every loaded domain state."""
    timestamp = considered_at or utc_timestamp()
    return [evaluate_domain_state(state, considered_at=timestamp) for state in domain_states]
