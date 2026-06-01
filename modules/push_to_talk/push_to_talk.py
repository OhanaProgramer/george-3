"""User-controlled push-to-talk flow.

Purpose: Manually start recording, manually stop recording, and transcribe it.
Phase: Push-To-Talk v1.
Last updated: 2026-05-31.
Notes: User-triggered only; no wake word, speaker ID, LLM, actions, or speech response.
"""

from __future__ import annotations

from shared.speech_to_text.transcription import transcribe_audio
from modules.voice_capture.voice_capture import start_capture, stop_capture


def run_push_to_talk(
    input_reader=input,
    output_writer=print,
    start_capture_runner=start_capture,
    stop_capture_runner=stop_capture,
    transcription_runner=transcribe_audio,
):
    output_writer("George 3 Push-To-Talk")
    output_writer("")
    input_reader("Press ENTER to start recording.")

    session = start_capture_runner()
    result = {
        "success": False,
        "capture": {},
        "transcription": {},
        "transcript": "",
        "message": "",
        "error": "",
    }

    if not session.get("success"):
        result["error"] = session.get("error") or "Voice capture failed to start."
        output_writer("")
        output_writer("Result: ERROR")
        output_writer("")
        output_writer(f"Error: {result['error']}")
        return result

    output_writer("")
    output_writer("Recording...")
    output_writer("")
    input_reader("Press ENTER to stop recording.")

    capture = stop_capture_runner(session)
    result["capture"] = capture

    if not capture.get("success"):
        result["error"] = capture.get("error") or "Voice capture failed."
        output_writer("")
        output_writer("Result: ERROR")
        output_writer("")
        output_writer(f"Error: {result['error']}")
        return result

    output_writer("")
    output_writer("Transcribing...")

    transcription = transcription_runner(capture.get("output_file"))
    result["transcription"] = transcription
    result["transcript"] = transcription.get("transcript", "")

    if not transcription.get("success"):
        result["error"] = transcription.get("error") or "Transcription failed."
        output_writer(format_push_to_talk_summary(result))
        return result

    result["success"] = True
    result["message"] = "Push-to-talk captured and transcribed audio."
    output_writer(format_push_to_talk_summary(result))
    return result


def format_push_to_talk_summary(result):
    transcript = result["transcript"] if result["transcript"] else "(none)"
    lines = [
        "",
        "Transcript:",
        "",
        transcript,
        "",
        f"Result: {'SUCCESS' if result['success'] else 'ERROR'}",
    ]

    if result["error"]:
        lines.extend(["", f"Error: {result['error']}"])

    return "\n".join(lines)


def main():
    run_push_to_talk()


if __name__ == "__main__":
    main()
