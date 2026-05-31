"""Apple voice speaking.

Purpose: Speak text using the configured Apple voice engine.
Phase: Voice Speak v1.
Last updated: 2026-05-31.
Notes: Uses macOS say only; no recording, transcription, wake word, or AI calls.
"""

from __future__ import annotations

import json
import subprocess
import sys

from config import settings


def run_command(command, timeout_seconds=30):
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout_seconds,
    )


def speak_text(text: str) -> dict:
    voice_name = settings.VOICE_NAME
    result = {
        "success": False,
        "engine": settings.VOICE_ENGINE,
        "voice": voice_name,
        "message": "",
        "error": "",
    }

    if settings.VOICE_ENGINE != "apple":
        result["error"] = f"Unsupported voice engine: {settings.VOICE_ENGINE}"
        return result

    if not text or not text.strip():
        result["error"] = "No text provided."
        return result

    command = ["say"]

    if voice_name:
        command.extend(["-v", voice_name])

    command.append(text)

    try:
        command_result = run_command(command)
    except subprocess.TimeoutExpired as exc:
        result["error"] = f"say timed out after {exc.timeout} seconds."
        return result
    except OSError as exc:
        result["error"] = str(exc)
        return result

    if command_result.returncode != 0:
        result["error"] = command_result.stderr.strip() or "say failed."
        return result

    result["success"] = True
    result["message"] = "Spoke text."
    return result


def main():
    text = " ".join(sys.argv[1:])
    print(json.dumps(speak_text(text), indent=2))


if __name__ == "__main__":
    main()
