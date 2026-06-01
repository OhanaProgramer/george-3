"""Audio file transcription.

Purpose: Convert an existing WAV file into text.
Phase: Transcription v1.
Last updated: 2026-05-31.
Notes: Reads one audio file and exits; no wake word, speaker ID, AI actions, or listening.
"""

from __future__ import annotations

import argparse
import subprocess
import wave
from pathlib import Path

from config import settings


DEFAULT_INPUT_FILE = Path("data/voice_capture/latest_capture.wav")
DEFAULT_OUTPUT_DIR = Path("data/transcription")


def run_command(command, timeout_seconds=120):
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout_seconds,
    )


def transcribe_audio(
    input_file=DEFAULT_INPUT_FILE,
    command_runner=run_command,
    output_dir=DEFAULT_OUTPUT_DIR,
):
    input_path = resolve_project_path(input_file)
    output_path = resolve_project_path(output_dir)
    input_label = format_project_path(input_path)
    transcript_file = output_path / f"{input_path.stem}.txt"

    result = {
        "success": False,
        "engine": settings.TRANSCRIPTION_ENGINE,
        "input_file": input_label,
        "transcript": "",
        "duration_seconds": read_wav_duration_seconds(input_path),
        "message": "",
        "error": "",
    }

    if settings.TRANSCRIPTION_ENGINE != "whisper_cli":
        result["error"] = f"Unsupported transcription engine: {settings.TRANSCRIPTION_ENGINE}"
        return result

    if not input_path.exists():
        result["error"] = "Input audio file was not found."
        return result

    output_path.mkdir(parents=True, exist_ok=True)
    command = build_transcription_command(input_path, output_path)

    try:
        command_result = command_runner(command, timeout_seconds=120)
    except subprocess.TimeoutExpired as exc:
        result["error"] = f"Transcription timed out after {exc.timeout} seconds."
        return result
    except OSError as exc:
        result["error"] = str(exc)
        return result

    if command_result.returncode != 0:
        result["error"] = command_result.stderr.strip() or "Transcription engine failed."
        return result

    if not transcript_file.exists():
        result["error"] = "Transcription engine did not produce a transcript file."
        return result

    transcript = transcript_file.read_text().strip()
    result["success"] = True
    result["transcript"] = transcript
    result["message"] = "Audio transcribed."
    return result


def build_transcription_command(input_path, output_dir):
    return [
        settings.TRANSCRIPTION_COMMAND,
        str(input_path),
        "--model",
        settings.TRANSCRIPTION_MODEL,
        "--language",
        settings.TRANSCRIPTION_LANGUAGE,
        "--output_format",
        "txt",
        "--output_dir",
        str(output_dir),
    ]


def read_wav_duration_seconds(input_path):
    if not input_path.exists():
        return None

    try:
        with wave.open(str(input_path), "rb") as wav_file:
            frame_count = wav_file.getnframes()
            frame_rate = wav_file.getframerate()
    except (wave.Error, OSError, EOFError):
        return None

    if not frame_rate:
        return None

    return round(frame_count / float(frame_rate), 3)


def resolve_project_path(path):
    resolved = Path(path)

    if resolved.is_absolute():
        return resolved

    return settings.PROJECT_ROOT / resolved


def format_project_path(path):
    try:
        return str(path.relative_to(settings.PROJECT_ROOT))
    except ValueError:
        return str(path)


def format_transcription_summary(result):
    transcript = result["transcript"] if result["transcript"] else "(none)"
    lines = [
        "George 3 Transcription",
        "",
        f"Engine: {result['engine']}",
        "Input File:",
        result["input_file"],
        "",
        "Transcript:",
        transcript,
        "",
        f"Result: {'SUCCESS' if result['success'] else 'ERROR'}",
    ]

    if result["error"]:
        lines.extend(["", f"Error: {result['error']}"])

    return "\n".join(lines)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Transcribe an existing George WAV file.")
    parser.add_argument("input_file", nargs="?", default=DEFAULT_INPUT_FILE)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    print(format_transcription_summary(transcribe_audio(args.input_file)))


if __name__ == "__main__":
    main()
