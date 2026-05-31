"""Voice capture tests.

Purpose: Verify one-shot audio capture structure and command behavior.
Phase: Voice Capture v1.
Last updated: 2026-05-31.
Notes: Uses fake discovery and command runners; does not record audio.
"""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from modules.voice_capture import voice_capture


def make_result(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def discovery_with_microphone(name="MacBook Pro Microphone"):
    return {
        "microphones": [
            {
                "name": name,
                "input_channels": 1,
            }
        ]
    }


class VoiceCaptureTests(unittest.TestCase):
    def test_object_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with (
                patch.object(voice_capture.settings, "PROJECT_ROOT", Path(tmpdir)),
                patch.object(voice_capture.settings, "VOICE_INPUT_DEVICE_HINT", "MacBook"),
                patch.object(voice_capture.settings, "GEORGE_ENV", "test"),
            ):
                result = voice_capture.capture_audio(
                    discovery_reader=discovery_with_microphone,
                    command_runner=lambda command, timeout_seconds=15: make_result(),
                )

        self.assertEqual(
            set(result.keys()),
            {
                "success",
                "input_device_hint",
                "input_device_found",
                "duration_seconds",
                "output_file",
                "message",
                "error",
            },
        )

    def test_successful_capture_path(self):
        commands = []

        def fake_runner(command, timeout_seconds=15):
            commands.append((command, timeout_seconds))
            return make_result()

        with tempfile.TemporaryDirectory() as tmpdir:
            with (
                patch.object(voice_capture.settings, "PROJECT_ROOT", Path(tmpdir)),
                patch.object(voice_capture.settings, "VOICE_INPUT_DEVICE_HINT", "MacBook"),
                patch.object(voice_capture.settings, "GEORGE_ENV", "test"),
            ):
                result = voice_capture.capture_audio(
                    discovery_reader=discovery_with_microphone,
                    command_runner=fake_runner,
                )

        self.assertTrue(result["success"])
        self.assertTrue(result["input_device_found"])
        self.assertEqual(result["message"], "Audio captured.")
        self.assertEqual(result["error"], "")
        self.assertEqual(commands[0][0][:6], ["ffmpeg", "-y", "-f", "avfoundation", "-i", ":MacBook Pro Microphone"])
        self.assertEqual(commands[0][1], 13)

    def test_missing_microphone_path(self):
        def empty_discovery():
            return {"microphones": []}

        with tempfile.TemporaryDirectory() as tmpdir:
            with (
                patch.object(voice_capture.settings, "PROJECT_ROOT", Path(tmpdir)),
                patch.object(voice_capture.settings, "VOICE_INPUT_DEVICE_HINT", "XVF3800"),
                patch.object(voice_capture.settings, "GEORGE_ENV", "test"),
            ):
                result = voice_capture.capture_audio(
                    discovery_reader=empty_discovery,
                    command_runner=lambda command, timeout_seconds=15: make_result(),
                )

        self.assertFalse(result["success"])
        self.assertFalse(result["input_device_found"])
        self.assertEqual(result["error"], "Configured input device was not found.")

    def test_output_file_path_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with (
                patch.object(voice_capture.settings, "PROJECT_ROOT", Path(tmpdir)),
                patch.object(voice_capture.settings, "VOICE_INPUT_DEVICE_HINT", "MacBook"),
                patch.object(voice_capture.settings, "GEORGE_ENV", "test"),
            ):
                result = voice_capture.capture_audio(
                    output_file=Path("data/voice_capture/custom.wav"),
                    discovery_reader=discovery_with_microphone,
                    command_runner=lambda command, timeout_seconds=15: make_result(),
                )

        self.assertEqual(result["output_file"], "data/voice_capture/custom.wav")

    def test_duration_parameter_handling(self):
        commands = []

        def fake_runner(command, timeout_seconds=15):
            commands.append((command, timeout_seconds))
            return make_result()

        with tempfile.TemporaryDirectory() as tmpdir:
            with (
                patch.object(voice_capture.settings, "PROJECT_ROOT", Path(tmpdir)),
                patch.object(voice_capture.settings, "VOICE_INPUT_DEVICE_HINT", "MacBook"),
                patch.object(voice_capture.settings, "GEORGE_ENV", "test"),
            ):
                result = voice_capture.capture_audio(
                    seconds=5,
                    discovery_reader=discovery_with_microphone,
                    command_runner=fake_runner,
                )

        self.assertEqual(result["duration_seconds"], 5)
        self.assertIn("-t", commands[0][0])
        self.assertEqual(commands[0][0][commands[0][0].index("-t") + 1], "5")
        self.assertEqual(commands[0][1], 15)


if __name__ == "__main__":
    unittest.main()
