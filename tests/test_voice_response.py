"""Voice response tests.

Purpose: Verify simple push-to-talk -> voice_speak orchestration.
Phase: Voice Response v1.
Last updated: 2026-05-31.
Notes: Uses fake runners; does not require a microphone, Whisper, or audio output.
"""

import unittest

from modules.voice_response import voice_response


def push_to_talk_result(success=True, transcript="George this is a test", error=""):
    return {
        "success": success,
        "capture": {"success": success},
        "transcription": {"success": success},
        "transcript": transcript if success else "",
        "message": "Push-to-talk captured and transcribed audio." if success else "",
        "error": error,
    }


def speak_result(success=True, error=""):
    return {
        "success": success,
        "engine": "apple",
        "voice": "Daniel",
        "message": "Spoke text." if success else "",
        "error": error,
    }


class VoiceResponseTests(unittest.TestCase):
    def test_object_shape(self):
        result = voice_response.run_voice_response(
            push_to_talk_runner=lambda: push_to_talk_result(),
            speak_runner=lambda text: speak_result(),
        )

        self.assertEqual(
            set(result.keys()),
            {
                "success",
                "push_to_talk",
                "spoken_response",
                "transcript",
                "response_text",
                "message",
                "error",
            },
        )

    def test_successful_voice_response(self):
        spoken = []

        result = voice_response.run_voice_response(
            push_to_talk_runner=lambda: push_to_talk_result(transcript="George this is a test"),
            speak_runner=lambda text: spoken.append(text) or speak_result(),
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["transcript"], "George this is a test")
        self.assertEqual(result["response_text"], "I heard: George this is a test")
        self.assertEqual(result["message"], "Voice response completed.")
        self.assertEqual(result["error"], "")
        self.assertEqual(spoken, ["I heard: George this is a test"])

    def test_push_to_talk_failure(self):
        def fail_if_called(text):
            raise AssertionError("speak should not be called")

        result = voice_response.run_voice_response(
            push_to_talk_runner=lambda: push_to_talk_result(success=False, error="No transcript"),
            speak_runner=fail_if_called,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["spoken_response"], {})
        self.assertEqual(result["response_text"], "")
        self.assertEqual(result["error"], "No transcript")

    def test_speak_failure(self):
        result = voice_response.run_voice_response(
            push_to_talk_runner=lambda: push_to_talk_result(transcript="George test"),
            speak_runner=lambda text: speak_result(success=False, error="say failed"),
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["response_text"], "I heard: George test")
        self.assertEqual(result["spoken_response"]["error"], "say failed")
        self.assertEqual(result["error"], "say failed")


if __name__ == "__main__":
    unittest.main()
