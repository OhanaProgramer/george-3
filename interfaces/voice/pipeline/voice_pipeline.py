"""Manual one-shot voice pipeline.

Purpose: Capture a short audio clip and transcribe it in one command.
Phase: Voice Pipeline v1.
Last updated: 2026-05-31.
Notes: Manual capture -> transcription only; no wake word, speaker ID, LLM, or actions.
"""

from __future__ import annotations

import argparse

from shared.speech_to_text.transcription import transcribe_audio
from interfaces.voice.capture.voice_capture import DEFAULT_DURATION_SECONDS, capture_audio


def run_voice_pipeline(
    seconds=DEFAULT_DURATION_SECONDS,
    capture_runner=capture_audio,
    transcription_runner=transcribe_audio,
):
    capture = capture_runner(seconds=seconds)
    result = {
        "success": False,
        "capture": capture,
        "transcription": {},
        "transcript": "",
        "message": "",
        "error": "",
    }

    if not capture.get("success"):
        result["error"] = capture.get("error") or "Voice capture failed."
        return result

    transcription = transcription_runner(capture.get("output_file"))
    result["transcription"] = transcription
    result["transcript"] = transcription.get("transcript", "")

    if not transcription.get("success"):
        result["error"] = transcription.get("error") or "Transcription failed."
        return result

    result["success"] = True
    result["message"] = "Voice captured and transcribed."
    return result


def format_pipeline_summary(result):
    transcript = result["transcript"] if result["transcript"] else "(none)"
    lines = [
        "George 3 Voice Pipeline",
        "",
        f"Capture: {format_step_status(result['capture'])}",
        f"Transcription: {format_step_status(result['transcription'])}",
        "",
        "Transcript:",
        transcript,
        "",
        f"Result: {'SUCCESS' if result['success'] else 'ERROR'}",
    ]

    if result["error"]:
        lines.extend(["", f"Error: {result['error']}"])

    return "\n".join(lines)


def format_step_status(step_result):
    if not step_result:
        return "SKIPPED"

    return "OK" if step_result.get("success") else "ERROR"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run manual George voice capture -> transcription.")
    parser.add_argument("--seconds", type=int, default=DEFAULT_DURATION_SECONDS)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    print(format_pipeline_summary(run_voice_pipeline(seconds=args.seconds)))


if __name__ == "__main__":
    main()
