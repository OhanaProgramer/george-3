"""Isolated speaker output test for George."""

from __future__ import annotations

import argparse
import sys

from config import settings
from shared.text_to_speech.voice_speak import speak_text


DEFAULT_PHRASE = "George speaker test successful."


def detected_output_intent() -> str:
    output_hint = settings.VOICE_OUTPUT_DEVICE_HINT

    if output_hint and output_hint != "system_default":
        return f"{output_hint} via configured macOS system output"

    return "configured macOS system output"


def run_speaker_test(phrase=DEFAULT_PHRASE, speak_runner=speak_text):
    result = {
        "success": False,
        "phrase": phrase,
        "output_intent": detected_output_intent(),
        "speech": {},
        "message": "",
        "error": "",
    }

    speech = speak_runner(phrase)
    result["speech"] = speech

    if not speech.get("success"):
        result["error"] = speech.get("error") or "Speaker test failed."
        return result

    result["success"] = True
    result["message"] = "Speaker test successful."
    return result


def format_speaker_test_summary(result):
    lines = [
        "George 3 Speaker Test",
        "",
        f"Detected output intent: {result['output_intent']}",
        f"Speaker test phrase: {result['phrase']}",
        f"Speech: {'OK' if result['speech'].get('success') else 'ERROR'}",
        "",
        f"Result: {'SUCCESS' if result['success'] else 'ERROR'}",
    ]

    if result["error"]:
        lines.extend(["", f"Error: {result['error']}"])

    return "\n".join(lines)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run an isolated George speaker output test.")
    parser.add_argument("phrase", nargs="?", default=DEFAULT_PHRASE)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    result = run_speaker_test(args.phrase)
    print(format_speaker_test_summary(result))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
