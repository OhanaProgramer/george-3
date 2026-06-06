import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from interfaces.voice import sonos_speaker_test


def completed(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(["say"], returncode, stdout, stderr)


class SonosSpeakerTestTests(unittest.TestCase):
    def test_generate_wav_uses_required_format(self):
        commands = []

        def fake_runner(command, timeout_seconds=15):
            commands.append(command)
            return completed()

        with tempfile.TemporaryDirectory() as tmpdir:
            result = sonos_speaker_test.generate_wav(
                "George test",
                Path(tmpdir) / "test.wav",
                command_runner=fake_runner,
            )

        self.assertTrue(result["success"])
        self.assertIn("--file-format=WAVE", commands[0])
        self.assertIn("--data-format=LEI16@44100", commands[0])

    def test_generate_wav_reports_say_error(self):
        result = sonos_speaker_test.generate_wav(
            "George test",
            Path("/tmp/missing.wav"),
            command_runner=lambda command, timeout_seconds=15: completed(
                returncode=1, stderr="say failed"
            ),
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "say failed")

    def test_playback_success_requires_playing_poll(self):
        class FakeSpeaker:
            player_name = "Den"
            volume = 44
            mute = False

            def play_uri(self, audio_url, title):
                self.audio_url = audio_url

            def get_current_transport_info(self):
                return {"current_transport_state": "PLAYING"}

            def get_current_track_info(self):
                return {"position": "0:00:01", "duration": "0:00:04"}

        fake_module = type("FakeSoCoModule", (), {"SoCo": lambda ip: FakeSpeaker()})

        with patch.dict("sys.modules", {"soco": fake_module}):
            result = sonos_speaker_test.play_sonos_url(
                "192.168.0.99",
                "http://127.0.0.1/test.wav",
                "George test",
                poll_seconds=1,
                sleeper=lambda seconds: None,
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["speaker_name"], "Den")


if __name__ == "__main__":
    unittest.main()
