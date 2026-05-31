"""Readiness status tests.

Purpose: Verify readiness aggregation behavior and failure handling.
Phase: Readiness Aggregator v1.
Last updated: 2026-05-31.
Notes: Uses fake module readers; does not call live system services.
"""

import unittest
from unittest.mock import patch

from modules.readiness import readiness_status


def system_detail(memory=16.0, disk_total=500.0, disk_free=250.0):
    return {
        "node": {
            "name": "macpro-dev",
            "role": "dev",
            "environment": "development",
        },
        "host": {
            "hostname": "MacBook.local",
            "os": "Darwin",
            "os_version": "macOS-test",
            "architecture": "arm64",
            "python_version": "3.14.5",
        },
        "resources": {
            "cpu_count": 16,
            "memory_total_gb": memory,
            "disk_total_gb": disk_total,
            "disk_free_gb": disk_free,
        },
        "paths": {
            "cwd": "/tmp/george-3",
            "project_root": "/tmp/george-3",
        },
        "timestamp": "now",
    }


def tailscale_detail(backend_state="Running", ip="100.64.1.2", installed=True):
    return {
        "installed": installed,
        "running": backend_state == "Running",
        "backend_state": backend_state,
        "tailscale_ip": ip,
    }


def voice_detail(
    input_found=True,
    output_found=True,
    apple_voices=None,
    configured_voice="",
    configured_voice_found=None,
    voice_engine="apple",
):
    if apple_voices is None:
        apple_voices = [{"name": "Samantha", "locale": "en_US"}]

    return {
        "voice_engine": voice_engine,
        "configured_voice": configured_voice,
        "configured_voice_found": configured_voice_found,
        "input_target_found": input_found,
        "output_target_found": output_found,
        "apple_voices": apple_voices,
    }


class ReadinessStatusTests(unittest.TestCase):
    def test_object_shape(self):
        readiness = readiness_status.get_readiness_status(
            system_reader=system_detail,
            tailscale_reader=tailscale_detail,
            voice_reader=voice_detail,
            timestamp_reader=lambda: "now",
        )

        self.assertEqual(set(readiness.keys()), {"overall_status", "checks", "details", "timestamp"})
        self.assertEqual(set(readiness["checks"].keys()), {"system", "tailscale", "voice"})
        self.assertEqual(set(readiness["details"].keys()), {"system", "tailscale", "voice"})

    def test_overall_ok(self):
        readiness = readiness_status.get_readiness_status(
            system_reader=system_detail,
            tailscale_reader=tailscale_detail,
            voice_reader=voice_detail,
            timestamp_reader=lambda: "now",
        )

        self.assertEqual(readiness["overall_status"], "ok")
        self.assertEqual(readiness["checks"]["system"]["status"], "ok")
        self.assertEqual(readiness["checks"]["tailscale"]["status"], "ok")
        self.assertEqual(readiness["checks"]["voice"]["status"], "ok")

    def test_warning_behavior(self):
        readiness = readiness_status.get_readiness_status(
            system_reader=lambda: system_detail(memory=None),
            tailscale_reader=tailscale_detail,
            voice_reader=voice_detail,
            timestamp_reader=lambda: "now",
        )

        self.assertEqual(readiness["overall_status"], "warning")
        self.assertEqual(readiness["checks"]["system"]["status"], "warning")

    def test_error_behavior(self):
        readiness = readiness_status.get_readiness_status(
            system_reader=system_detail,
            tailscale_reader=lambda: tailscale_detail(ip=None),
            voice_reader=voice_detail,
            timestamp_reader=lambda: "now",
        )

        self.assertEqual(readiness["overall_status"], "error")
        self.assertEqual(readiness["checks"]["tailscale"]["status"], "error")

    def test_module_failure_does_not_crash_aggregator(self):
        def broken_reader():
            raise RuntimeError("boom")

        readiness = readiness_status.get_readiness_status(
            system_reader=system_detail,
            tailscale_reader=broken_reader,
            voice_reader=voice_detail,
            timestamp_reader=lambda: "now",
        )

        self.assertEqual(readiness["overall_status"], "error")
        self.assertEqual(readiness["checks"]["tailscale"]["status"], "error")
        self.assertIn("module failed", readiness["checks"]["tailscale"]["summary"])

    def test_summary_is_clean(self):
        readiness = readiness_status.get_readiness_status(
            system_reader=system_detail,
            tailscale_reader=tailscale_detail,
            voice_reader=voice_detail,
            timestamp_reader=lambda: "now",
        )

        summary = readiness_status.format_readiness_summary(readiness)

        self.assertIn("George 3 Readiness Status", summary)
        self.assertIn("Overall: OK", summary)
        self.assertIn("Tailscale: OK", summary)
        self.assertIn("Voice: OK", summary)
        self.assertIn("  Devices: OK", summary)
        self.assertIn("  Speak config: OK", summary)

    def test_voice_readiness_ok_with_blank_voice_name(self):
        voice_check = readiness_status.evaluate_voice(voice_detail(configured_voice=""))

        self.assertEqual(voice_check["status"], "ok")
        self.assertEqual(voice_check["devices"]["status"], "ok")
        self.assertEqual(voice_check["speak_config"]["status"], "ok")

    def test_voice_readiness_ok_when_configured_apple_voice_exists(self):
        voice_check = readiness_status.evaluate_voice(
            voice_detail(configured_voice="Samantha", configured_voice_found=True)
        )

        self.assertEqual(voice_check["status"], "ok")
        self.assertEqual(voice_check["speak_config"]["status"], "ok")

    def test_voice_readiness_error_when_configured_apple_voice_is_missing(self):
        voice_check = readiness_status.evaluate_voice(
            voice_detail(configured_voice="MissingVoice", configured_voice_found=False)
        )

        self.assertEqual(voice_check["status"], "error")
        self.assertEqual(voice_check["speak_config"]["status"], "error")
        self.assertIn("Configured Apple voice was not found", voice_check["summary"])

    def test_readiness_does_not_call_speak_text(self):
        with patch("modules.voice.voice_speak.speak_text", side_effect=AssertionError("called speak_text")):
            readiness = readiness_status.get_readiness_status(
                system_reader=system_detail,
                tailscale_reader=tailscale_detail,
                voice_reader=voice_detail,
                timestamp_reader=lambda: "now",
            )

        self.assertEqual(readiness["checks"]["voice"]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
