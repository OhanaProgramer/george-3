"""Transcription tests.

Purpose: Verify audio-to-text result structure and engine handling.
Phase: Transcription v1.
Last updated: 2026-05-31.
Notes: Uses fake files and command runners; does not require real audio or Whisper.
"""

import tempfile
import unittest
import wave
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from shared.speech_to_text import transcription


def make_result(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def write_test_wav(path):
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b"\x00\x00" * 16000)


class TranscriptionTests(unittest.TestCase):
    @contextmanager
    def transcription_settings(self, project_root):
        with (
            patch.object(transcription.settings, "PROJECT_ROOT", project_root),
            patch.object(transcription.settings, "TRANSCRIPTION_ENGINE", "whisper_cli"),
            patch.object(transcription.settings, "TRANSCRIPTION_COMMAND", "whisper"),
            patch.object(transcription.settings, "TRANSCRIPTION_MODEL", "base"),
            patch.object(transcription.settings, "TRANSCRIPTION_LANGUAGE", "en"),
        ):
            yield

    def test_object_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            input_file = project_root / "data/voice_capture/latest_capture.wav"

            with self.transcription_settings(project_root):
                result = transcription.transcribe_audio(input_file=input_file)

        self.assertEqual(
            set(result.keys()),
            {
                "success",
                "engine",
                "input_file",
                "transcript",
                "duration_seconds",
                "message",
                "error",
            },
        )

    def test_missing_file_handling(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            with self.transcription_settings(project_root):
                result = transcription.transcribe_audio(input_file="data/voice_capture/missing.wav")

        self.assertFalse(result["success"])
        self.assertEqual(result["input_file"], "data/voice_capture/missing.wav")
        self.assertEqual(result["duration_seconds"], None)
        self.assertEqual(result["error"], "Input audio file was not found.")

    def test_successful_transcription_path(self):
        commands = []

        def fake_runner(command, timeout_seconds=120):
            commands.append((command, timeout_seconds))
            output_dir = Path(command[command.index("--output_dir") + 1])
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "latest_capture.txt").write_text("Hello George this is a transcription test.\n")
            return make_result()

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            input_file = project_root / "data/voice_capture/latest_capture.wav"
            input_file.parent.mkdir(parents=True)
            write_test_wav(input_file)

            with self.transcription_settings(project_root):
                result = transcription.transcribe_audio(
                    input_file="data/voice_capture/latest_capture.wav",
                    command_runner=fake_runner,
                )

        self.assertTrue(result["success"])
        self.assertEqual(result["engine"], "whisper_cli")
        self.assertEqual(result["input_file"], "data/voice_capture/latest_capture.wav")
        self.assertEqual(result["transcript"], "Hello George this is a transcription test.")
        self.assertEqual(result["duration_seconds"], 1.0)
        self.assertEqual(result["message"], "Audio transcribed.")
        self.assertEqual(result["error"], "")
        self.assertEqual(commands[0][0][0], "whisper")
        self.assertEqual(commands[0][0][commands[0][0].index("--model") + 1], "base")
        self.assertEqual(commands[0][0][commands[0][0].index("--language") + 1], "en")
        self.assertEqual(commands[0][1], 120)

    def test_engine_failure_path(self):
        def fake_runner(command, timeout_seconds=120):
            return make_result(returncode=1, stderr="whisper failed")

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            input_file = project_root / "data/voice_capture/latest_capture.wav"
            input_file.parent.mkdir(parents=True)
            write_test_wav(input_file)

            with self.transcription_settings(project_root):
                result = transcription.transcribe_audio(
                    input_file="data/voice_capture/latest_capture.wav",
                    command_runner=fake_runner,
                )

        self.assertFalse(result["success"])
        self.assertEqual(result["transcript"], "")
        self.assertEqual(result["error"], "whisper failed")

    def test_unsupported_engine_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            with (
                patch.object(transcription.settings, "PROJECT_ROOT", project_root),
                patch.object(transcription.settings, "TRANSCRIPTION_ENGINE", "apple_speech"),
            ):
                result = transcription.transcribe_audio(input_file="data/voice_capture/latest_capture.wav")

        self.assertFalse(result["success"])
        self.assertEqual(result["engine"], "apple_speech")
        self.assertEqual(result["error"], "Unsupported transcription engine: apple_speech")


if __name__ == "__main__":
    unittest.main()
