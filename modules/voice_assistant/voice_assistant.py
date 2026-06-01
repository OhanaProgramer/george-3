"""Voice assistant orchestration.

Purpose: Hear a spoken request, think with the configured LLM, and speak the response.
Phase: Voice Assistant v1.
Last updated: 2026-05-31.
Notes: Hear -> think -> speak only; no wake word, memory, tools, actions, or remote control.
"""

from __future__ import annotations

from modules.push_to_talk.push_to_talk import run_push_to_talk
from modules.voice.voice_speak import speak_text
from shared.llm.llm_adapter import ask_llm


def run_voice_assistant(
    push_to_talk_runner=run_push_to_talk,
    llm_runner=ask_llm,
    speak_runner=speak_text,
):
    push_to_talk = push_to_talk_runner()
    result = {
        "success": False,
        "transcript": push_to_talk.get("transcript", ""),
        "llm_response": "",
        "capture": push_to_talk.get("capture", {}),
        "transcription": push_to_talk.get("transcription", {}),
        "llm": {},
        "speech": {},
        "message": "",
        "error": "",
    }

    if not push_to_talk.get("success"):
        result["error"] = push_to_talk.get("error") or "Push-to-talk failed."
        return result

    llm = llm_runner(result["transcript"])
    result["llm"] = llm
    result["llm_response"] = llm.get("response_text", "")

    if not llm.get("success"):
        result["error"] = llm.get("error") or "LLM request failed."
        return result

    speech = speak_runner(result["llm_response"])
    result["speech"] = speech

    if not speech.get("success"):
        result["error"] = speech.get("error") or "Speech output failed."
        return result

    result["success"] = True
    result["message"] = "Voice assistant completed."
    return result


def format_voice_assistant_summary(result):
    transcript = result["transcript"] if result["transcript"] else "(none)"
    llm_response = result["llm_response"] if result["llm_response"] else "(none)"
    lines = [
        "George 3 Voice Assistant",
        "",
        f"Capture: {format_step_status(result['capture'])}",
        f"Transcription: {format_step_status(result['transcription'])}",
        f"LLM: {format_step_status(result['llm'])}",
        f"Speech: {format_step_status(result['speech'])}",
        "",
        "Transcript:",
        transcript,
        "",
        "Response:",
        llm_response,
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
    print(format_voice_assistant_summary(run_voice_assistant()))


if __name__ == "__main__":
    main()
