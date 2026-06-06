import unittest

from interfaces.voice import mic_speaker_loop_test


def capture_result(success=True, error=""):
    return {
        "success": success,
        "error": error,
        "file": {"exists": success, "path": "/tmp/george_mic_test.wav"},
    }


def speech_result(success=True, error=""):
    return {
        "success": success,
        "message": "Spoke text." if success else "",
        "error": error,
    }


class MicSpeakerLoopTestTests(unittest.TestCase):
    def test_local_loop_success(self):
        spoken = []

        result = mic_speaker_loop_test.run_mic_speaker_loop_test(
            output="local",
            capture_runner=lambda seconds, output_file: capture_result(),
            local_speaker=lambda phrase: spoken.append(phrase) or speech_result(),
        )

        self.assertTrue(result["success"])
        self.assertEqual(spoken, ["I heard audio. Anya loop test successful."])

    def test_sonos_loop_success(self):
        spoken = []

        result = mic_speaker_loop_test.run_mic_speaker_loop_test(
            output="sonos",
            capture_runner=lambda seconds, output_file: capture_result(),
            sonos_speaker=lambda phrase: spoken.append(phrase) or speech_result(),
        )

        self.assertTrue(result["success"])
        self.assertEqual(spoken, ["I heard audio. Anya loop test successful."])

    def test_capture_failure_stops_before_speech(self):
        result = mic_speaker_loop_test.run_mic_speaker_loop_test(
            capture_runner=lambda seconds, output_file: capture_result(False, "capture failed"),
            local_speaker=lambda phrase: speech_result(),
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["speech"], {})
        self.assertEqual(result["error"], "capture failed")


if __name__ == "__main__":
    unittest.main()
