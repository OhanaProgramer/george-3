"""Speaker output test tests.

Purpose: Verify isolated speaker test orchestration.
Phase: Speaker Test v1.
Last updated: 2026-06-04.
Notes: Uses fake speech output; does not play audio, record, transcribe, or call AI.
"""

import unittest
from unittest.mock import patch

from interfaces.voice import speaker_test


def speech_result(success=True, error=""):
    return {
        "success": success,
        "engine": "apple",
        "voice": "",
        "message": "Spoke text." if success else "",
        "error": error,
    }


class SpeakerTestTests(unittest.TestCase):
    def test_successful_speaker_test(self):
        spoken = []

        result = speaker_test.run_speaker_test(
            speak_runner=lambda text: spoken.append(text) or speech_result()
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["phrase"], "George speaker test successful.")
        self.assertEqual(result["message"], "Speaker test successful.")
        self.assertEqual(result["error"], "")
        self.assertEqual(spoken, ["George speaker test successful."])

    def test_custom_phrase(self):
        spoken = []

        result = speaker_test.run_speaker_test(
            phrase="Testing Mini Mac speaker output.",
            speak_runner=lambda text: spoken.append(text) or speech_result(),
        )

        self.assertTrue(result["success"])
        self.assertEqual(spoken, ["Testing Mini Mac speaker output."])

    def test_speaker_test_failure(self):
        result = speaker_test.run_speaker_test(
            speak_runner=lambda text: speech_result(success=False, error="say failed")
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "say failed")

    def test_detected_output_intent_uses_output_hint(self):
        with patch.object(speaker_test.settings, "VOICE_OUTPUT_DEVICE_HINT", "Den"):
            result = speaker_test.run_speaker_test(speak_runner=lambda text: speech_result())

        self.assertEqual(result["output_intent"], "Den via configured macOS system output")

    def test_main_returns_success_status(self):
        with patch.object(
            speaker_test,
            "run_speaker_test",
            lambda phrase: {
                "success": True,
                "phrase": phrase,
                "output_intent": "configured macOS system output",
                "speech": {"success": True},
                "message": "Speaker test successful.",
                "error": "",
            },
        ):
            result = speaker_test.main(["Testing Mini Mac speaker output."])

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
