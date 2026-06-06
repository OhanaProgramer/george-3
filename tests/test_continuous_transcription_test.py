import tempfile
import threading
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from interfaces.voice import continuous_transcription_test


def discovery():
    return {"microphones": [{"name": "reSpeaker XVF3800 4-Mic Array"}]}


def capture_success(seconds, output_file):
    Path(output_file).write_bytes(b"fake wav")
    return {"success": True, "error": ""}


def write_wav(path, sample_value=0):
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(sample_value.to_bytes(2, "little", signed=True) * 16000)


class ContinuousTranscriptionTestTests(unittest.TestCase):
    def test_continuous_loop_prints_non_empty_transcripts(self):
        output = []
        captured_files = []

        def capture(seconds, output_file):
            captured_files.append(Path(output_file))
            return capture_success(seconds, output_file)

        def transcribe(input_file):
            return {
                "success": True,
                "input_file": str(input_file),
                "transcript": "testing one two three",
                "error": "",
            }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = continuous_transcription_test.run_continuous_transcription_test(
                tmp_dir=Path(tmpdir),
                stop_event=threading.Event(),
                capture_runner=capture,
                transcription_runner=transcribe,
                discovery_reader=discovery,
                output_writer=output.append,
                max_chunks=1,
                show_files=True,
                level_reader=lambda path: {"success": True, "rms_dbfs": -20.0, "max_dbfs": -10.0},
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["transcripts"], ["testing one two three"])
        self.assertEqual(captured_files[0].parent, Path(result["run_dir"]))
        self.assertIn("Transcript: testing one two three", output)
        self.assertTrue(any(line.startswith("Audio file:") for line in output))
        self.assertTrue(any(line.startswith("Transcript source:") for line in output))

    def test_empty_transcripts_are_ignored(self):
        output = []

        with tempfile.TemporaryDirectory() as tmpdir:
            result = continuous_transcription_test.run_continuous_transcription_test(
                tmp_dir=Path(tmpdir),
                stop_event=threading.Event(),
                capture_runner=capture_success,
                transcription_runner=lambda input_file: {"success": True, "transcript": " ", "error": ""},
                discovery_reader=discovery,
                output_writer=output.append,
                max_chunks=1,
                level_reader=lambda path: {"success": True, "rms_dbfs": -20.0, "max_dbfs": -10.0},
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["transcripts"], [])
        self.assertFalse(any(line.startswith("Transcript:") for line in output))

    def test_capture_failure_continues_until_limit(self):
        output = []

        with tempfile.TemporaryDirectory() as tmpdir:
            result = continuous_transcription_test.run_continuous_transcription_test(
                tmp_dir=Path(tmpdir),
                stop_event=threading.Event(),
                capture_runner=lambda seconds, output_file: {"success": False, "error": "capture failed"},
                transcription_runner=lambda input_file: {"success": True, "transcript": "unused"},
                discovery_reader=discovery,
                output_writer=output.append,
                max_chunks=1,
                level_reader=lambda path: {"success": True, "rms_dbfs": -20.0, "max_dbfs": -10.0},
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["errors"], ["capture failed"])
        self.assertIn("Capture error: capture failed", output)

    def test_silent_chunk_skips_transcription(self):
        output = []
        transcribe_calls = []

        with tempfile.TemporaryDirectory() as tmpdir:
            result = continuous_transcription_test.run_continuous_transcription_test(
                tmp_dir=Path(tmpdir),
                stop_event=threading.Event(),
                capture_runner=capture_success,
                transcription_runner=lambda input_file: transcribe_calls.append(input_file),
                discovery_reader=discovery,
                output_writer=output.append,
                max_chunks=1,
                show_files=True,
                level_reader=lambda path: {"success": True, "rms_dbfs": -120.0, "max_dbfs": -120.0},
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["skipped_silence"], 1)
        self.assertEqual(transcribe_calls, [])
        self.assertIn("Silence detected; skipping transcription.", output)

    def test_measure_wav_level_for_silent_wav(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_file = Path(tmpdir) / "silent.wav"
            write_wav(audio_file, sample_value=0)

            level = continuous_transcription_test.measure_wav_level(audio_file)

        self.assertTrue(level["success"])
        self.assertEqual(level["rms_dbfs"], -120.0)
        self.assertEqual(level["max_dbfs"], -120.0)

    def test_measure_wav_level_for_non_silent_wav(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_file = Path(tmpdir) / "tone.wav"
            write_wav(audio_file, sample_value=1000)

            level = continuous_transcription_test.measure_wav_level(audio_file)

        self.assertTrue(level["success"])
        self.assertGreater(level["rms_dbfs"], -55.0)

    def test_wait_for_key_sets_stop_event_for_tty(self):
        stop_event = threading.Event()

        class FakeTTY:
            def isatty(self):
                return True

            def fileno(self):
                return 0

            def read(self, size):
                return "x"

        original_tcgetattr = continuous_transcription_test.termios.tcgetattr
        original_tcsetattr = continuous_transcription_test.termios.tcsetattr
        original_setcbreak = continuous_transcription_test.tty.setcbreak

        continuous_transcription_test.termios.tcgetattr = lambda fd: "settings"
        continuous_transcription_test.termios.tcsetattr = lambda fd, when, settings: None
        continuous_transcription_test.tty.setcbreak = lambda fd: None

        try:
            continuous_transcription_test.wait_for_key(
                stop_event,
                input_stream=FakeTTY(),
                output_writer=lambda line: None,
            )
        finally:
            continuous_transcription_test.termios.tcgetattr = original_tcgetattr
            continuous_transcription_test.termios.tcsetattr = original_tcsetattr
            continuous_transcription_test.tty.setcbreak = original_setcbreak

        self.assertTrue(stop_event.is_set())

    def test_parse_whisper_cpp_output_without_timestamps(self):
        transcript = continuous_transcription_test.parse_whisper_cpp_output(
            " testing one two three\n\n another phrase\n"
        )

        self.assertEqual(transcript, "testing one two three another phrase")

    def test_parse_whisper_cpp_output_with_timestamps(self):
        transcript = continuous_transcription_test.parse_whisper_cpp_output(
            "[00:00:00.000 --> 00:00:02.000] testing one two three\n"
        )

        self.assertEqual(transcript, "testing one two three")

    def test_transcribe_audio_for_test_builds_whisper_cpp_command(self):
        commands = []

        def fake_runner(command, timeout_seconds=120):
            commands.append((command, timeout_seconds))
            return SimpleNamespace(returncode=0, stdout=" testing one two three\n", stderr="")

        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "chunk.wav"
            model_file = Path(tmpdir) / "ggml-base.en.bin"
            input_file.write_bytes(b"fake wav")
            model_file.write_bytes(b"fake model")

            result = continuous_transcription_test.transcribe_audio_for_test(
                input_file,
                model_file=model_file,
                whisper_command="whisper-cli",
                command_runner=fake_runner,
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["engine"], "whisper.cpp")
        self.assertEqual(result["transcript"], "testing one two three")
        self.assertEqual(commands[0][0][0], "whisper-cli")
        self.assertIn("-m", commands[0][0])
        self.assertIn("-f", commands[0][0])

    def test_transcribe_audio_for_test_requires_model_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "chunk.wav"
            input_file.write_bytes(b"fake wav")

            result = continuous_transcription_test.transcribe_audio_for_test(
                input_file,
                model_file=Path(tmpdir) / "missing.bin",
            )

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "whisper.cpp model file was not found.")

    def test_continuous_loop_defaults_input_hint(self):
        with patch.object(continuous_transcription_test.settings, "VOICE_INPUT_DEVICE_HINT", ""):
            hint = continuous_transcription_test.ensure_input_hint()

        self.assertEqual(hint, "reSpeaker")


if __name__ == "__main__":
    unittest.main()
