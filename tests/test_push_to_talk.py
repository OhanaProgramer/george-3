"""Push-to-talk tests.

Purpose: Verify user-triggered capture -> transcription orchestration.
Phase: Push-To-Talk v1.
Last updated: 2026-05-31.
Notes: Uses fake runners; does not require a microphone, WAV file, or Whisper.
"""

import unittest

from modules.push_to_talk import push_to_talk


def capture_session(success=True, error=""):
    return {
        "success": success,
        "input_device_hint": "Test Microphone",
        "input_device_found": success,
        "output_file": "data/voice_capture/latest_capture.wav",
        "process": object() if success else None,
        "started_at": 0.0 if success else None,
        "message": "Audio capture started." if success else "",
        "error": error,
    }


def capture_result(success=True, error=""):
    return {
        "success": success,
        "input_device_hint": "Test Microphone",
        "input_device_found": success,
        "duration_seconds": 2.0,
        "output_file": "data/voice_capture/latest_capture.wav",
        "message": "Audio captured." if success else "",
        "error": error,
    }


def transcription_result(success=True, transcript="George what is the weather tomorrow?", error=""):
    return {
        "success": success,
        "engine": "whisper_cli",
        "input_file": "data/voice_capture/latest_capture.wav",
        "transcript": transcript if success else "",
        "duration_seconds": 2.0,
        "message": "Audio transcribed." if success else "",
        "error": error,
    }


class PushToTalkTests(unittest.TestCase):
    def test_object_shape(self):
        result = push_to_talk.run_push_to_talk(
            input_reader=lambda prompt="": "",
            output_writer=lambda message="": None,
            start_capture_runner=lambda: capture_session(),
            stop_capture_runner=lambda session: capture_result(),
            transcription_runner=lambda input_file: transcription_result(),
        )

        self.assertEqual(
            set(result.keys()),
            {
                "success",
                "capture",
                "transcription",
                "transcript",
                "message",
                "error",
            },
        )

    def test_successful_path(self):
        prompts = []
        output_files = []

        def fake_input(prompt=""):
            prompts.append(prompt)
            return ""

        result = push_to_talk.run_push_to_talk(
            input_reader=fake_input,
            output_writer=lambda message="": None,
            start_capture_runner=lambda: capture_session(),
            stop_capture_runner=lambda session: capture_result(),
            transcription_runner=lambda input_file: output_files.append(input_file) or transcription_result(),
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["transcript"], "George what is the weather tomorrow?")
        self.assertEqual(result["message"], "Push-to-talk captured and transcribed audio.")
        self.assertEqual(result["error"], "")
        self.assertEqual(prompts, ["Press ENTER to start recording.", "Press ENTER to stop recording."])
        self.assertEqual(output_files, ["data/voice_capture/latest_capture.wav"])

    def test_capture_failure(self):
        def fail_if_called(session):
            raise AssertionError("stop_capture should not be called")

        result = push_to_talk.run_push_to_talk(
            input_reader=lambda prompt="": "",
            output_writer=lambda message="": None,
            start_capture_runner=lambda: capture_session(success=False, error="No microphone"),
            stop_capture_runner=fail_if_called,
            transcription_runner=lambda input_file: transcription_result(),
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["capture"], {})
        self.assertEqual(result["transcription"], {})
        self.assertEqual(result["error"], "No microphone")

    def test_transcription_failure(self):
        result = push_to_talk.run_push_to_talk(
            input_reader=lambda prompt="": "",
            output_writer=lambda message="": None,
            start_capture_runner=lambda: capture_session(),
            stop_capture_runner=lambda session: capture_result(),
            transcription_runner=lambda input_file: transcription_result(success=False, error="Whisper failed"),
        )

        self.assertFalse(result["success"])
        self.assertTrue(result["capture"]["success"])
        self.assertEqual(result["transcription"]["error"], "Whisper failed")
        self.assertEqual(result["transcript"], "")
        self.assertEqual(result["error"], "Whisper failed")


if __name__ == "__main__":
    unittest.main()
