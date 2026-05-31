"""Learning-first Tailscale visibility check."""

from __future__ import annotations

import json
import shutil
import subprocess

from config import settings


def run_command(command, timeout_seconds=settings.TAILSCALE_TIMEOUT_SECONDS):
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout_seconds,
    )


def is_tailscale_installed():
    return shutil.which("tailscale") is not None


def get_tailscale_ip(command_runner=run_command):
    result = command_runner(["tailscale", "ip", "-4"])

    if result.returncode != 0:
        return None

    ip_lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return ip_lines[0] if ip_lines else None


def get_tailscale_status(command_runner=run_command):
    installed = is_tailscale_installed()
    status = {
        "node_name": settings.GEORGE_NODE_NAME,
        "node_role": settings.GEORGE_NODE_ROLE,
        "tailscale_expected": settings.TAILSCALE_EXPECTED,
        "installed": installed,
        "running": False,
        "backend_state": "unknown",
        "tailscale_ip": None,
        "ok": False,
        "message": "",
    }

    if not installed:
        status["ok"] = not settings.TAILSCALE_EXPECTED
        status["message"] = "Tailscale is not installed."
        return status

    result = command_runner(["tailscale", "status", "--json"])

    if result.returncode != 0:
        status["message"] = clean_error(result.stderr) or "Tailscale is installed but not responding."
        return status

    try:
        status_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        status["message"] = "Tailscale returned status data George could not read."
        return status

    status["backend_state"] = status_data.get("BackendState", "unknown")
    status["running"] = status["backend_state"] == "Running"
    status["tailscale_ip"] = get_tailscale_ip(command_runner)
    status["ok"] = status["running"] if settings.TAILSCALE_EXPECTED else True

    if status["running"]:
        status["message"] = "Tailscale is running."
    else:
        status["message"] = f"Tailscale backend state is {status['backend_state']}."

    return status


def clean_error(error_text):
    return " ".join(error_text.split())


def format_status_summary(status):
    return "\n".join(
        [
            "George 3 Tailscale Status",
            f"Node: {status['node_name']} ({status['node_role']})",
            f"Tailscale expected: {'yes' if status['tailscale_expected'] else 'no'}",
            f"Installed: {'yes' if status['installed'] else 'no'}",
            f"Running: {'yes' if status['running'] else 'no'}",
            f"Backend state: {status['backend_state']}",
            f"Tailscale IP: {status['tailscale_ip'] or 'not available'}",
            f"OK: {'yes' if status['ok'] else 'no'}",
            f"Message: {status['message']}",
        ]
    )


def main():
    print(format_status_summary(get_tailscale_status()))


if __name__ == "__main__":
    main()
