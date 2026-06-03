"""George Core developer view CLI.

Purpose: Show how George Core reads and evaluates domain analytics.
Phase: George Core Dev View v1.
Last updated: 2026-06-03.
Notes: Temporary developer visibility; read-only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.george_core import domain_reader, evaluator


def get_core_evaluations(project_root: Path | None = None) -> list[dict[str, Any]]:
    """Return current Core evaluations for all discovered domains."""
    states = domain_reader.load_domain_states(project_root=project_root)
    return evaluator.evaluate_domain_states(states)


def format_evaluations(evaluations: list[dict[str, Any]]) -> str:
    """Return a concise terminal-friendly Core dev view."""
    lines = ["George Core Dev View", ""]

    if not evaluations:
        lines.extend(["No domain analytics files found.", "Result: SUCCESS"])
        return "\n".join(lines)

    for index, evaluation in enumerate(evaluations):
        if index:
            lines.append("")

        lines.extend(
            [
                f"Domain: {evaluation.get('domain', '')}",
                f"Core Response: {evaluation.get('core_response', '')}",
                f"Status: {evaluation.get('status', '')}",
                f"Reason: {evaluation.get('reason', '')}",
                f"Last considered: {evaluation.get('last_considered_at', '')}",
                f"Generated at: {evaluation.get('generated_at', '')}",
                "Signals reviewed:",
            ]
        )

        signals = evaluation.get("signals_reviewed") or {}
        if signals:
            for key, value in signals.items():
                lines.append(f"- {key}: {value}")
        else:
            lines.append("- none")

        significant = evaluation.get("significant_signals") or []
        if significant:
            lines.append("Significant signals:")
            for signal in significant:
                lines.append(f"- {signal}")

    lines.extend(["", "Result: SUCCESS"])
    return "\n".join(lines)


def main() -> None:
    print(format_evaluations(get_core_evaluations()))


if __name__ == "__main__":
    main()
