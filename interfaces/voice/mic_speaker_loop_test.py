"""Isolated microphone capture plus fixed speaker response test."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable, Sequence

from interfaces.voice.mic_capture_test import DEFAULT_OUTPUT_FILE, run_mic_capture_test
from interfaces.voice.sonos_speaker_test import run_sonos_speaker_test
from shared.text_to_speech.voice_speak import speak_text


DEFAULT_RESPONSE_PHRASE = "I heard audio. Anya loop test successful."


def speak_local(phrase: str) -> dict:
    return speak_text(phrase)


def speak_sonos(phrase: str) -> dict:
    return run_sonos_speaker_test(phrase=phrase)


def run_mic_speaker_loop_test(
    output: str = "local",
    seconds: int = 3,
    capture_runner: Callable = run_mic_capture_test,
    local_speaker: Callable = speak_local,
    sonos_speaker: Callable = speak_sonos,
) -> dict:
    result = {
        "success": False,
        "output": output,
        "seconds": seconds,
        "capture": {},
        "speech": {},
        "phrase": DEFAULT_RESPONSE_PHRASE,
        "message": "",
        "error": "",
    }

    capture = capture_runner(seconds=seconds, output_file=DEFAULT_OUTPUT_FILE)
    result["capture"] = capture

    if not capture.get("success"):
        result["error"] = capture.get("error") or "Mic capture failed."
        return result

    if output == "local":
        speech = local_speaker(DEFAULT_RESPONSE_PHRASE)
    elif output == "sonos":
        speech = sonos_speaker(DEFAULT_RESPONSE_PHRASE)
    else:
        result["error"] = f"Unsupported output backend: {output}"
        return result

    result["speech"] = speech

    if not speech.get("success"):
        result["error"] = speech.get("error") or "Speaker output failed."
        return result

    result["success"] = True
    result["message"] = "Mic speaker loop test successful."
    return result


def format_mic_speaker_loop_summary(result: dict) -> str:
    lines = [
        "George 3 Mic Speaker Loop Test",
        "",
        f"Capture duration: {result['seconds']} seconds",
        f"Output backend: {result['output']}",
        f"Response phrase: {result['phrase']}",
        f"Capture: {'OK' if result['capture'].get('success') else 'ERROR'}",
        f"Speech: {'OK' if result['speech'].get('success') else 'ERROR'}",
        "",
        f"Result: {'SUCCESS' if result['success'] else 'ERROR'}",
    ]

    if result["message"]:
        lines.append(f"Message: {result['message']}")

    if result["error"]:
        lines.append(f"Error: {result['error']}")

    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(description="Run isolated mic capture plus fixed speaker response.")
    parser.add_argument("--output", choices=["local", "sonos"], default="local")
    parser.add_argument("--seconds", type=int, default=3)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_mic_speaker_loop_test(output=args.output, seconds=args.seconds)
    print(format_mic_speaker_loop_summary(result))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
