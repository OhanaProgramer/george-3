"""One-shot voice capture.

Purpose: Capture a short audio sample from the configured microphone.
Phase: Voice Capture v1.
Last updated: 2026-05-31.
Notes: One capture and exit; no wake word, transcription, speaker ID, or AI.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from config import settings
from modules.voice.voice_devices import discover_voice_devices, has_name_match


DEFAULT_DURATION_SECONDS = 3
DEFAULT_OUTPUT_FILE = Path("data/voice_capture/latest_capture.wav")


def run_command(command, timeout_seconds=15):
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout_seconds,
    )


def capture_audio(
    seconds=DEFAULT_DURATION_SECONDS,
    output_file=DEFAULT_OUTPUT_FILE,
    discovery_reader=discover_voice_devices,
    command_runner=run_command,
):
    duration_seconds = int(seconds)
    output_path = resolve_output_path(output_file)
    output_label = format_output_path(output_path)
    input_device_hint = settings.VOICE_INPUT_DEVICE_HINT
    _environment = settings.GEORGE_ENV

    result = {
        "success": False,
        "input_device_hint": input_device_hint,
        "input_device_found": False,
        "duration_seconds": duration_seconds,
        "output_file": output_label,
        "message": "",
        "error": "",
    }

    if duration_seconds <= 0:
        result["error"] = "Duration must be greater than 0 seconds."
        return result

    discovery = discovery_reader()
    microphone = find_input_device(discovery.get("microphones", []), input_device_hint)

    if not microphone:
        result["error"] = "Configured input device was not found."
        return result

    result["input_device_found"] = True
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = build_capture_command(microphone["name"], duration_seconds, output_path)

    try:
        command_result = command_runner(command, timeout_seconds=duration_seconds + 10)
    except subprocess.TimeoutExpired as exc:
        result["error"] = f"Audio capture timed out after {exc.timeout} seconds."
        return result
    except OSError as exc:
        result["error"] = str(exc)
        return result

    if command_result.returncode != 0:
        result["error"] = command_result.stderr.strip() or "Audio capture failed."
        return result

    result["success"] = True
    result["message"] = "Audio captured."
    return result


def find_input_device(microphones, input_device_hint):
    for microphone in microphones:
        if has_name_match([microphone], input_device_hint):
            return microphone

    return None


def build_capture_command(input_device_name, duration_seconds, output_path):
    return [
        "ffmpeg",
        "-y",
        "-f",
        "avfoundation",
        "-i",
        f":{input_device_name}",
        "-t",
        str(duration_seconds),
        "-ac",
        "1",
        "-ar",
        "16000",
        str(output_path),
    ]


def resolve_output_path(output_file):
    output_path = Path(output_file)

    if output_path.is_absolute():
        return output_path

    return settings.PROJECT_ROOT / output_path


def format_output_path(output_path):
    try:
        return str(output_path.relative_to(settings.PROJECT_ROOT))
    except ValueError:
        return str(output_path)


def format_capture_summary(result):
    return "\n".join(
        [
            "George 3 Voice Capture",
            "",
            f"Input Device: {result['input_device_hint']}",
            f"Input Found: {'YES' if result['input_device_found'] else 'NO'}",
            f"Duration: {result['duration_seconds']} seconds",
            "Output File:",
            result["output_file"],
            "",
            f"Result: {'SUCCESS' if result['success'] else 'ERROR'}",
        ]
    )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Capture a short George voice audio sample.")
    parser.add_argument("--seconds", type=int, default=DEFAULT_DURATION_SECONDS)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    print(format_capture_summary(capture_audio(seconds=args.seconds)))


if __name__ == "__main__":
    main()
