"""Simple voice response pipeline.

Purpose: Hear a manually triggered utterance and speak back a confirmation.
Phase: Voice Response v1.
Last updated: 2026-05-31.
Notes: No LLM, wake word, speaker ID, conversation memory, actions, or remote control.
"""

from __future__ import annotations

from interfaces.voice.push_to_talk.push_to_talk import run_push_to_talk
from shared.text_to_speech.voice_speak import speak_text


def run_voice_response(
    push_to_talk_runner=run_push_to_talk,
    speak_runner=speak_text,
):
    push_to_talk = push_to_talk_runner()
    result = {
        "success": False,
        "push_to_talk": push_to_talk,
        "spoken_response": {},
        "transcript": push_to_talk.get("transcript", ""),
        "response_text": "",
        "message": "",
        "error": "",
    }

    if not push_to_talk.get("success"):
        result["error"] = push_to_talk.get("error") or "Push-to-talk failed."
        return result

    response_text = build_confirmation_response(push_to_talk.get("transcript", ""))
    result["response_text"] = response_text
    spoken_response = speak_runner(response_text)
    result["spoken_response"] = spoken_response

    if not spoken_response.get("success"):
        result["error"] = spoken_response.get("error") or "Voice response failed."
        return result

    result["success"] = True
    result["message"] = "Voice response completed."
    return result


def build_confirmation_response(transcript):
    return f"I heard: {transcript.strip()}"


def format_voice_response_summary(result):
    transcript = result["transcript"] if result["transcript"] else "(none)"
    response_text = result["response_text"] if result["response_text"] else "(none)"
    lines = [
        "George 3 Voice Response",
        "",
        f"Push-To-Talk: {format_step_status(result['push_to_talk'])}",
        f"Voice Speak: {format_step_status(result['spoken_response'])}",
        "",
        "Transcript:",
        transcript,
        "",
        "Spoken Response:",
        response_text,
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


def main():
    print(format_voice_response_summary(run_voice_response()))


if __name__ == "__main__":
    main()
