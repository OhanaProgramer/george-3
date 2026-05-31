"""George 3 configuration loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"


def load_env_file(env_file=ENV_FILE):
    """Load simple KEY=VALUE lines without printing or exposing secrets."""
    if not env_file.exists():
        return

    for raw_line in env_file.read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()

GEORGE_NODE_NAME = os.getenv("GEORGE_NODE_NAME", "unknown-node")
GEORGE_NODE_ROLE = os.getenv("GEORGE_NODE_ROLE", "dev")
GEORGE_ENV = os.getenv("GEORGE_ENV", "development")
GEORGE_LOG_LEVEL = os.getenv("GEORGE_LOG_LEVEL", "info")

TAILSCALE_EXPECTED = os.getenv("TAILSCALE_EXPECTED", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
TAILSCALE_TIMEOUT_SECONDS = int(os.getenv("TAILSCALE_TIMEOUT_SECONDS", "5"))


def as_dict():
    return {
        "project_root": str(PROJECT_ROOT),
        "george_node_name": GEORGE_NODE_NAME,
        "george_node_role": GEORGE_NODE_ROLE,
        "george_env": GEORGE_ENV,
        "george_log_level": GEORGE_LOG_LEVEL,
        "tailscale_expected": TAILSCALE_EXPECTED,
        "tailscale_timeout_seconds": TAILSCALE_TIMEOUT_SECONDS,
    }


if __name__ == "__main__":
    for key, value in as_dict().items():
        print(f"{key}={value}")
