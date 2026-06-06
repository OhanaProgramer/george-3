"""Isolated Apple Music control proof for George."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from collections.abc import Callable, Sequence


ActionRunner = Callable[[str], subprocess.CompletedProcess[str]]
Sleeper = Callable[[float], None]


DEFAULT_SEQUENCE = (
    ("play", 5),
    ("pause", 2),
    ("play", 5),
    ("next track", 5),
    ("pause", 0),
)


def run_osascript(script: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            check=False,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            args=exc.cmd,
            returncode=124,
            stdout=exc.stdout or "",
            stderr=f"osascript timed out after {exc.timeout} seconds.",
        )


def verify_music_app(command_runner: ActionRunner = run_osascript) -> dict:
    script = 'id of application "Music"'
    result = command_runner(script)

    return {
        "success": result.returncode == 0,
        "music_available": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def run_music_action(action: str, command_runner: ActionRunner = run_osascript) -> dict:
    result = command_runner(f'tell application "Music" to {action}')

    return {
        "action": action,
        "success": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def run_music_control_test(
    sequence=DEFAULT_SEQUENCE,
    command_runner: ActionRunner = run_osascript,
    sleeper: Sleeper = time.sleep,
) -> dict:
    result = {
        "success": False,
        "app": {},
        "actions": [],
        "message": "",
        "error": "",
    }

    app = verify_music_app(command_runner)
    result["app"] = app

    if not app["success"]:
        result["error"] = app["stderr"] or "Could not verify Music.app."
        return result

    for action, wait_seconds in sequence:
        action_result = run_music_action(action, command_runner)
        result["actions"].append(action_result)

        if not action_result["success"]:
            result["error"] = action_result["stderr"] or f"Music action failed: {action}"
            return result

        if wait_seconds:
            sleeper(wait_seconds)

    result["success"] = True
    result["message"] = "Apple Music control test completed."
    return result


def format_command_result(label: str, command_result: dict) -> list[str]:
    lines = [
        f"{label}:",
        f"  return code: {command_result['returncode']}",
    ]

    if "music_available" in command_result:
        lines.append(f"  music available: {command_result['music_available']}")

    if command_result.get("stdout"):
        lines.append(f"  stdout: {command_result['stdout']}")

    if command_result.get("stderr"):
        lines.append(f"  stderr: {command_result['stderr']}")

    return lines


def format_music_control_summary(result: dict) -> str:
    lines = [
        "George 3 Apple Music Control Test",
        "",
        "Assumption: Music.app output has already been manually routed to Den through AirPlay.",
        "This test does not select or automate AirPlay output.",
        "",
    ]

    lines.extend(format_command_result("Verify Music.app", result["app"]))

    for action in result["actions"]:
        lines.extend(["", f"Action: {action['action']}"])
        lines.extend(format_command_result("Command result", action))

    lines.extend(["", f"Result: {'SUCCESS' if result['success'] else 'ERROR'}"])

    if result["message"]:
        lines.append(f"Message: {result['message']}")

    if result["error"]:
        lines.append(f"Error: {result['error']}")

    if result["success"]:
        lines.extend(
            [
                "",
                "Conclusion:",
                "Voice Output: George WAV -> SoCo -> Den",
                "Music Playback: Music.app -> AirPlay Den",
                "George controls Music.app orchestration.",
            ]
        )

    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(description="Run an isolated Apple Music control test.")
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Run commands without waits. Intended for tests only.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    sleeper = (lambda seconds: None) if args.no_wait else time.sleep
    result = run_music_control_test(sleeper=sleeper)
    print(format_music_control_summary(result))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
