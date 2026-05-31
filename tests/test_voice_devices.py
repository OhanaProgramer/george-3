"""Voice device discovery tests.

Purpose: Verify audio device and Apple voice discovery normalization.
Phase: Voice Discovery v1.
Last updated: 2026-05-31.
Notes: Uses fake macOS command output; does not record or play audio.
"""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from config import settings
from modules.voice import voice_devices


def make_result(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


class VoiceDevicesTests(unittest.TestCase):
    def test_settings_expose_voice_config(self):
        self.assertEqual(settings.VOICE_ENGINE, "apple")
        self.assertIsInstance(settings.VOICE_NAME, str)
        self.assertIsInstance(settings.VOICE_INPUT_DEVICE_HINT, str)
        self.assertIsInstance(settings.VOICE_OUTPUT_DEVICE_HINT, str)
        self.assertIsInstance(settings.VOICE_PRODUCTION_SPEAKER_HINT, str)

    def test_hint_matching_is_case_insensitive(self):
        items = [{"name": "reSpeaker XVF3800 4-Mic Array"}]

        self.assertTrue(voice_devices.has_name_match(items, "xvf3800"))
        self.assertFalse(voice_devices.has_name_match(items, "not-present"))

    def test_object_shape_with_fake_devices(self):
        audio_payload = {
            "SPAudioDataType": [
                {
                    "_items": [
                        {
                            "_name": "reSpeaker XVF3800 4-Mic Array",
                            "coreaudio_device_input": 2,
                            "coreaudio_device_output": 0,
                            "coreaudio_device_manufacturer": "Seeed Studio",
                        },
                        {
                            "_name": "MacBook Pro Speakers",
                            "coreaudio_device_output": 2,
                            "coreaudio_default_audio_system_device": "spaudio_yes",
                            "coreaudio_device_manufacturer": "Apple Inc.",
                        },
                    ]
                }
            ]
        }

        def fake_runner(command):
            if command == ["system_profiler", "SPAudioDataType", "-json"]:
                return make_result(stdout=json.dumps(audio_payload))
            if command == ["say", "-v", "?"]:
                return make_result(stdout="Samantha           en_US    # Hello\n")
            raise AssertionError(f"Unexpected command: {command}")

        with (
            patch.object(settings, "VOICE_INPUT_DEVICE_HINT", "XVF3800"),
            patch.object(settings, "VOICE_OUTPUT_DEVICE_HINT", "system_default"),
        ):
            discovery = voice_devices.discover_voice_devices(fake_runner)

        expected_keys = {
            "voice_engine",
            "configured_voice",
            "configured_voice_found",
            "input_device_hint",
            "input_target_found",
            "output_device_hint",
            "output_target_found",
            "production_speaker_hint",
            "microphones",
            "speakers",
            "apple_voices",
        }
        self.assertEqual(set(discovery.keys()), expected_keys)
        self.assertTrue(discovery["input_target_found"])
        self.assertTrue(discovery["output_target_found"])
        self.assertEqual(discovery["microphones"][0]["name"], "reSpeaker XVF3800 4-Mic Array")
        self.assertEqual(discovery["apple_voices"][0]["name"], "Samantha")

    def test_empty_or_missing_device_lists_are_safe(self):
        def fake_runner(command):
            if command == ["system_profiler", "SPAudioDataType", "-json"]:
                return make_result(stdout='{"SPAudioDataType": []}')
            if command == ["say", "-v", "?"]:
                return make_result(returncode=1, stderr="say unavailable")
            raise AssertionError(f"Unexpected command: {command}")

        discovery = voice_devices.discover_voice_devices(fake_runner)

        self.assertEqual(discovery["microphones"], [])
        self.assertEqual(discovery["speakers"], [])
        self.assertEqual(discovery["apple_voices"], [])
        self.assertFalse(discovery["input_target_found"])

    def test_configured_voice_found_when_voice_name_is_set(self):
        voices = [{"name": "Samantha", "locale": "en_US"}]

        self.assertTrue(voice_devices.has_name_match(voices, "Samantha"))


if __name__ == "__main__":
    unittest.main()
