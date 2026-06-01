"""Voice pipeline tests.

Purpose: Verify manual capture -> transcription orchestration.
Phase: Voice Pipeline v1.
Last updated: 2026-05-31.
Notes: Uses fake runners; does not require a microphone, WAV file, or Whisper.
"""

import unittest

from interfaces.voice.pipeline import voice_pipeline


def capture_result(success=True, output_file="data/voice_capture/latest_capture.wav", error=""):
    return {
        "success": success,
        "input_device_hint": "Test Microphone",
        "input_device_found": success,
        "duration_seconds": 3,
        "output_file": output_file,
        "message": "Audio captured." if success else "",
        "error": error,
    }


def transcription_result(success=True, transcript="George what time is it?", error=""):
    return {
        "success": success,
        "engine": "whisper_cli",
        "input_file": "data/voice_capture/latest_capture.wav",
        "transcript": transcript if success else "",
        "duration_seconds": 3.0,
        "message": "Audio transcribed." if success else "",
        "error": error,
    }


class VoicePipelineTests(unittest.TestCase):
    def test_object_shape(self):
        result = voice_pipeline.run_voice_pipeline(
            capture_runner=lambda seconds=3: capture_result(),
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

    def test_successful_pipeline(self):
        seen = {}

        def fake_capture(seconds=3):
            seen["seconds"] = seconds
            return capture_result(output_file="data/voice_capture/custom.wav")

        def fake_transcription(input_file):
            seen["input_file"] = input_file
            return transcription_result(transcript="George what time is it?")

        result = voice_pipeline.run_voice_pipeline(
            seconds=5,
            capture_runner=fake_capture,
            transcription_runner=fake_transcription,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["transcript"], "George what time is it?")
        self.assertEqual(result["message"], "Voice captured and transcribed.")
        self.assertEqual(result["error"], "")
        self.assertEqual(seen["seconds"], 5)
        self.assertEqual(seen["input_file"], "data/voice_capture/custom.wav")

    def test_capture_failure_stops_cleanly(self):
        def fail_if_called(input_file):
            raise AssertionError("transcription should not be called")

        result = voice_pipeline.run_voice_pipeline(
            capture_runner=lambda seconds=3: capture_result(success=False, error="No microphone"),
            transcription_runner=fail_if_called,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["transcription"], {})
        self.assertEqual(result["transcript"], "")
        self.assertEqual(result["error"], "No microphone")

    def test_transcription_failure_returns_structured_error(self):
        result = voice_pipeline.run_voice_pipeline(
            capture_runner=lambda seconds=3: capture_result(),
            transcription_runner=lambda input_file: transcription_result(success=False, error="Whisper missing"),
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["transcription"]["error"], "Whisper missing")
        self.assertEqual(result["transcript"], "")
        self.assertEqual(result["error"], "Whisper missing")


if __name__ == "__main__":
    unittest.main()
