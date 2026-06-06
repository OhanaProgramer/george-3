"""One-shot voice capture.

Purpose: Capture a short audio sample from the configured microphone.
Phase: Voice Capture v1.
Last updated: 2026-05-31.
Notes: One capture and exit; no wake word, transcription, speaker ID, or AI.
"""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

from config import settings
from shared.audio_devices.voice_devices import discover_voice_devices, has_name_match


DEFAULT_DURATION_SECONDS = 3
DEFAULT_OUTPUT_FILE = Path("data/voice_capture/latest_capture.wav")
FFMPEG_CANDIDATES = (
    Path("/usr/local/bin/ffmpeg"),
    Path("/opt/homebrew/bin/ffmpeg"),
)


def ffmpeg_command():
    for candidate in FFMPEG_CANDIDATES:
        if candidate.exists():
            return str(candidate)

    return "ffmpeg"


def run_command(command, timeout_seconds=15):
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout_seconds,
    )


def start_process(command):
    return subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
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


def start_capture(
    output_file=DEFAULT_OUTPUT_FILE,
    discovery_reader=discover_voice_devices,
    process_starter=start_process,
    time_reader=time.monotonic,
):
    output_path = resolve_output_path(output_file)
    output_label = format_output_path(output_path)
    input_device_hint = settings.VOICE_INPUT_DEVICE_HINT

    session = {
        "success": False,
        "input_device_hint": input_device_hint,
        "input_device_found": False,
        "output_file": output_label,
        "process": None,
        "started_at": None,
        "message": "",
        "error": "",
    }

    discovery = discovery_reader()
    microphone = find_input_device(discovery.get("microphones", []), input_device_hint)

    if not microphone:
        session["error"] = "Configured input device was not found."
        return session

    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = build_manual_capture_command(microphone["name"], output_path)

    try:
        process = process_starter(command)
    except OSError as exc:
        session["error"] = str(exc)
        return session

    session["success"] = True
    session["input_device_found"] = True
    session["process"] = process
    session["started_at"] = time_reader()
    session["message"] = "Audio capture started."
    return session


def stop_capture(session, time_reader=time.monotonic, timeout_seconds=5):
    duration_seconds = None

    if session.get("started_at") is not None:
        duration_seconds = round(max(0, time_reader() - session["started_at"]), 3)

    result = {
        "success": False,
        "input_device_hint": session.get("input_device_hint", ""),
        "input_device_found": bool(session.get("input_device_found")),
        "duration_seconds": duration_seconds,
        "output_file": session.get("output_file", str(DEFAULT_OUTPUT_FILE)),
        "message": "",
        "error": "",
    }

    if not session.get("success"):
        result["error"] = session.get("error") or "Audio capture did not start."
        return result

    process = session.get("process")

    if process is None:
        result["error"] = "Audio capture process was missing."
        return result

    try:
        if process.poll() is None and process.stdin:
            process.stdin.write("q\n")
            process.stdin.flush()
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        process.terminate()
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except OSError as exc:
        result["error"] = str(exc)
        return result

    if process.returncode != 0:
        result["error"] = (stderr or stdout or "Audio capture failed.").strip()
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
        ffmpeg_command(),
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


def build_manual_capture_command(input_device_name, output_path):
    return [
        ffmpeg_command(),
        "-y",
        "-f",
        "avfoundation",
        "-i",
        f":{input_device_name}",
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
