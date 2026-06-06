"""Apple Music control proof tests.

Purpose: Verify isolated Music.app command orchestration.
Phase: Apple Music Control Test v1.
Last updated: 2026-06-05.
Notes: Uses fake osascript results; does not control Music.app or audio output.
"""

import subprocess
import unittest
from contextlib import redirect_stdout
from io import StringIO

from interfaces.tests import music_control_test


def completed(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(
        args=["osascript"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


class MusicControlTestTests(unittest.TestCase):
    def test_successful_music_control_sequence(self):
        scripts = []
        sleeps = []

        def fake_runner(script):
            scripts.append(script)
            if script == 'id of application "Music"':
                return completed(stdout="com.apple.Music\n")
            return completed()

        result = music_control_test.run_music_control_test(
            command_runner=fake_runner,
            sleeper=sleeps.append,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Apple Music control test completed.")
        self.assertEqual(
            [action["action"] for action in result["actions"]],
            ["play", "pause", "play", "next track", "pause"],
        )
        self.assertEqual(sleeps, [5, 2, 5, 5])
        self.assertIn('tell application "Music" to next track', scripts)

    def test_music_verification_failure_stops_test(self):
        result = music_control_test.run_music_control_test(
            command_runner=lambda script: completed(returncode=1, stderr="No automation access"),
            sleeper=lambda seconds: None,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["actions"], [])
        self.assertEqual(result["error"], "No automation access")

    def test_action_failure_stops_test(self):
        def fake_runner(script):
            if script == 'id of application "Music"':
                return completed(stdout="com.apple.Music\n")
            if "pause" in script:
                return completed(returncode=1, stderr="Music command failed")
            return completed()

        result = music_control_test.run_music_control_test(
            command_runner=fake_runner,
            sleeper=lambda seconds: None,
        )

        self.assertFalse(result["success"])
        self.assertEqual(len(result["actions"]), 2)
        self.assertEqual(result["error"], "Music command failed")

    def test_action_timeout_stops_test(self):
        def fake_runner(script):
            if script == 'id of application "Music"':
                return completed(stdout="com.apple.Music\n")
            return completed(returncode=124, stderr="osascript timed out after 10 seconds.")

        result = music_control_test.run_music_control_test(
            command_runner=fake_runner,
            sleeper=lambda seconds: None,
        )

        self.assertFalse(result["success"])
        self.assertEqual(len(result["actions"]), 1)
        self.assertEqual(result["error"], "osascript timed out after 10 seconds.")

    def test_run_osascript_timeout_returns_structured_failure(self):
        original_run = music_control_test.subprocess.run

        def fake_run(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd=args[0], timeout=10)

        music_control_test.subprocess.run = fake_run
        try:
            result = music_control_test.run_osascript('tell application "Music" to play')
        finally:
            music_control_test.subprocess.run = original_run

        self.assertEqual(result.returncode, 124)
        self.assertEqual(result.stderr, "osascript timed out after 10 seconds.")

    def test_main_returns_success_status(self):
        def fake_run_music_control_test(sleeper):
            return {
                "success": True,
                "app": {
                    "returncode": 0,
                    "music_available": True,
                    "stdout": "com.apple.Music",
                    "stderr": "",
                },
                "actions": [],
                "message": "Apple Music control test completed.",
                "error": "",
            }

        original = music_control_test.run_music_control_test
        music_control_test.run_music_control_test = fake_run_music_control_test
        try:
            with redirect_stdout(StringIO()):
                result = music_control_test.main(["--no-wait"])
        finally:
            music_control_test.run_music_control_test = original

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
