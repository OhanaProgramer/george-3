"""George Core domain analytics reader.

Purpose: Load domain analytics.json files for Core evaluation.
Phase: George Core Dev View v1.
Last updated: 2026-06-03.
Notes: Reads derived domain state only; never reads raw event logs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ANALYTICS_RELATIVE_PATH = Path("data") / "analytics.json"


def get_project_root() -> Path:
    """Return the George 3 project root inferred from this package."""
    return PROJECT_ROOT


def discover_domain_dirs(project_root: Path | None = None) -> list[Path]:
    """Return domain directories in stable name order."""
    root = project_root or get_project_root()
    domains_root = root / "domains"
    if not domains_root.exists():
        return []

    return sorted(path for path in domains_root.iterdir() if path.is_dir())


def expected_analytics_path(domain_dir: Path) -> Path:
    """Return the expected analytics.json path for a domain directory."""
    return domain_dir / ANALYTICS_RELATIVE_PATH


def load_domain_state(domain_dir: Path) -> dict[str, Any]:
    """Load one domain analytics state safely."""
    analytics_path = expected_analytics_path(domain_dir)
    domain_name = domain_dir.name

    if not analytics_path.exists():
        return {
            "domain": domain_name,
            "path": str(analytics_path),
            "load_status": "missing",
            "data": {},
            "error": "analytics.json not found",
        }

    try:
        data = json.loads(analytics_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return {
            "domain": domain_name,
            "path": str(analytics_path),
            "load_status": "malformed",
            "data": {},
            "error": f"analytics.json is malformed: {error.msg}",
        }

    if not isinstance(data, dict):
        return {
            "domain": domain_name,
            "path": str(analytics_path),
            "load_status": "malformed",
            "data": {},
            "error": "analytics.json root is not an object",
        }

    return {
        "domain": str(data.get("domain") or domain_name),
        "path": str(analytics_path),
        "load_status": "loaded",
        "data": data,
        "error": "",
    }


def load_domain_states(project_root: Path | None = None) -> list[dict[str, Any]]:
    """Load every known domain analytics state."""
    return [load_domain_state(domain_dir) for domain_dir in discover_domain_dirs(project_root)]
