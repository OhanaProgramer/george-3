"""Isolated microphone capture test for George."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, Sequence

from interfaces.voice.capture.voice_capture import capture_audio
from shared.audio_devices.voice_devices import discover_voice_devices


DEFAULT_SECONDS = 3
DEFAULT_OUTPUT_FILE = Path("/tmp/george_mic_test.wav")
LOCAL_TOOL_PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"


def run_command(command, timeout_seconds=8):
    env = os.environ.copy()
    env["PATH"] = LOCAL_TOOL_PATH
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout_seconds,
        env=env,
    )


def capture_audio_for_test(seconds: int, output_file: Path):
    return capture_audio(seconds=seconds, output_file=output_file, command_runner=run_command)


def inspect_audio_file(output_file: Path, command_runner: Callable = run_command) -> dict:
    result = {
        "exists": output_file.exists(),
        "path": str(output_file),
        "size_bytes": output_file.stat().st_size if output_file.exists() else 0,
        "duration_seconds": None,
        "error": "",
    }

    if not result["exists"]:
        result["error"] = "Capture file was not created."
        return result

    try:
        command_result = command_runner(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(output_file),
            ],
            timeout_seconds=8,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        result["error"] = str(exc)
        return result

    if command_result.returncode == 0 and command_result.stdout.strip():
        try:
            result["duration_seconds"] = round(float(command_result.stdout.strip()), 3)
        except ValueError:
            result["error"] = "Could not parse ffprobe duration."
    elif command_result.stderr.strip():
        result["error"] = command_result.stderr.strip()

    return result


def run_mic_capture_test(
    seconds: int = DEFAULT_SECONDS,
    output_file: Path = DEFAULT_OUTPUT_FILE,
    discovery_reader: Callable = discover_voice_devices,
    capture_runner: Callable = capture_audio_for_test,
    inspector: Callable = inspect_audio_file,
) -> dict:
    discovery = discovery_reader()
    capture = capture_runner(seconds=seconds, output_file=output_file)
    inspection = inspector(Path(output_file))

    result = {
        "success": False,
        "seconds": seconds,
        "microphones": discovery.get("microphones", []),
        "capture": capture,
        "file": inspection,
        "message": "",
        "error": "",
    }

    if not capture.get("success"):
        result["error"] = capture.get("error") or "Mic capture failed."
        return result

    if not inspection.get("exists"):
        result["error"] = inspection.get("error") or "Capture file was not created."
        return result

    result["success"] = True
    result["message"] = "Mic capture test successful."
    return result


def format_mic_capture_summary(result: dict) -> str:
    lines = [
        "George 3 Mic Capture Test",
        "",
        f"Duration requested: {result['seconds']} seconds",
        f"Microphone count: {len(result['microphones'])}",
        "Input devices:",
    ]

    if result["microphones"]:
        lines.extend(f"- {device.get('name', 'unknown')}" for device in result["microphones"])
    else:
        lines.append("- none found")

    capture = result["capture"]
    file_info = result["file"]
    lines.extend(
        [
            "",
            f"Input hint: {capture.get('input_device_hint', '')}",
            f"Input found: {'YES' if capture.get('input_device_found') else 'NO'}",
            f"Capture: {'OK' if capture.get('success') else 'ERROR'}",
            f"Output file: {file_info['path']}",
            f"File exists: {'YES' if file_info['exists'] else 'NO'}",
            f"File size: {file_info['size_bytes']} bytes",
            f"File duration: {file_info['duration_seconds']} seconds",
            "",
            f"Result: {'SUCCESS' if result['success'] else 'ERROR'}",
        ]
    )

    if result["message"]:
        lines.append(f"Message: {result['message']}")

    if result["error"]:
        lines.append(f"Error: {result['error']}")

    if file_info.get("error") and file_info["error"] != result["error"]:
        lines.append(f"File note: {file_info['error']}")

    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(description="Run an isolated microphone capture test.")
    parser.add_argument("--seconds", type=int, default=DEFAULT_SECONDS)
    parser.add_argument("--output-file", default=str(DEFAULT_OUTPUT_FILE))
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_mic_capture_test(seconds=args.seconds, output_file=Path(args.output_file))
    print(format_mic_capture_summary(result))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
