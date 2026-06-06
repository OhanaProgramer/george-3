import tempfile
import unittest
from pathlib import Path

from interfaces.voice import mic_capture_test


def discovery():
    return {"microphones": [{"name": "reSpeaker XVF3800 4-Mic Array"}]}


def capture(success=True, error=""):
    return {
        "success": success,
        "input_device_hint": "XVF3800",
        "input_device_found": success,
        "duration_seconds": 3,
        "output_file": "/tmp/george_mic_test.wav",
        "message": "Audio captured." if success else "",
        "error": error,
    }


class MicCaptureTestTests(unittest.TestCase):
    def test_successful_mic_capture_test(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "capture.wav"
            output.write_bytes(b"fake wav")

            result = mic_capture_test.run_mic_capture_test(
                output_file=output,
                discovery_reader=discovery,
                capture_runner=lambda seconds, output_file: capture(),
                inspector=lambda output_file: {
                    "exists": True,
                    "path": str(output),
                    "size_bytes": 8,
                    "duration_seconds": 3.0,
                    "error": "",
                },
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Mic capture test successful.")

    def test_capture_failure(self):
        result = mic_capture_test.run_mic_capture_test(
            discovery_reader=discovery,
            capture_runner=lambda seconds, output_file: capture(False, "missing mic"),
            inspector=lambda output_file: {
                "exists": False,
                "path": str(output_file),
                "size_bytes": 0,
                "duration_seconds": None,
                "error": "missing file",
            },
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "missing mic")


if __name__ == "__main__":
    unittest.main()
