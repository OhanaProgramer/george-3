"""Voice speaking tests.

Purpose: Verify Apple say command construction and structured results.
Phase: Voice Speak v1.
Last updated: 2026-05-31.
Notes: Uses fake command output; does not speak, record, transcribe, or call AI.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.voice import voice_speak


def make_result(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


class VoiceSpeakTests(unittest.TestCase):
    def test_speak_text_uses_configured_apple_voice(self):
        commands = []

        def fake_runner(command):
            commands.append(command)
            return make_result()

        with (
            patch.object(voice_speak.settings, "VOICE_ENGINE", "apple"),
            patch.object(voice_speak.settings, "VOICE_NAME", "Samantha"),
            patch.object(voice_speak, "run_command", fake_runner),
        ):
            result = voice_speak.speak_text("George voice test")

        self.assertEqual(commands, [["say", "-v", "Samantha", "George voice test"]])
        self.assertEqual(
            result,
            {
                "success": True,
                "engine": "apple",
                "voice": "Samantha",
                "message": "Spoke text.",
                "error": "",
            },
        )

    def test_speak_text_uses_system_default_when_voice_name_is_blank(self):
        commands = []

        def fake_runner(command):
            commands.append(command)
            return make_result()

        with (
            patch.object(voice_speak.settings, "VOICE_ENGINE", "apple"),
            patch.object(voice_speak.settings, "VOICE_NAME", ""),
            patch.object(voice_speak, "run_command", fake_runner),
        ):
            result = voice_speak.speak_text("George voice test")

        self.assertEqual(commands, [["say", "George voice test"]])
        self.assertTrue(result["success"])
        self.assertEqual(result["voice"], "")

    def test_speak_text_rejects_unsupported_engine(self):
        with patch.object(voice_speak.settings, "VOICE_ENGINE", "other"):
            result = voice_speak.speak_text("George voice test")

        self.assertFalse(result["success"])
        self.assertEqual(result["engine"], "other")
        self.assertEqual(result["error"], "Unsupported voice engine: other")

    def test_speak_text_rejects_blank_text(self):
        with patch.object(voice_speak.settings, "VOICE_ENGINE", "apple"):
            result = voice_speak.speak_text("   ")

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "No text provided.")

    def test_speak_text_returns_say_error(self):
        def fake_runner(command):
            return make_result(returncode=1, stderr="Voice not found")

        with (
            patch.object(voice_speak.settings, "VOICE_ENGINE", "apple"),
            patch.object(voice_speak.settings, "VOICE_NAME", "MissingVoice"),
            patch.object(voice_speak, "run_command", fake_runner),
        ):
            result = voice_speak.speak_text("George voice test")

        self.assertFalse(result["success"])
        self.assertEqual(result["voice"], "MissingVoice")
        self.assertEqual(result["error"], "Voice not found")


if __name__ == "__main__":
    unittest.main()
