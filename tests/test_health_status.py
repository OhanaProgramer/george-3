import unittest

from modules.health import health_status


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


def voice_detail(input_found=True, output_found=True, apple_voices=None):
    if apple_voices is None:
        apple_voices = [{"name": "Samantha", "locale": "en_US"}]

    return {
        "voice_engine": "apple",
        "configured_voice": "",
        "configured_voice_found": None,
        "input_target_found": input_found,
        "output_target_found": output_found,
        "apple_voices": apple_voices,
    }


class HealthStatusTests(unittest.TestCase):
    def test_object_shape(self):
        health = health_status.get_health_status(
            system_reader=system_detail,
            tailscale_reader=tailscale_detail,
            voice_reader=voice_detail,
            timestamp_reader=lambda: "now",
        )

        self.assertEqual(set(health.keys()), {"overall_status", "checks", "details", "timestamp"})
        self.assertEqual(set(health["checks"].keys()), {"system", "tailscale", "voice"})
        self.assertEqual(set(health["details"].keys()), {"system", "tailscale", "voice"})

    def test_overall_ok(self):
        health = health_status.get_health_status(
            system_reader=system_detail,
            tailscale_reader=tailscale_detail,
            voice_reader=voice_detail,
            timestamp_reader=lambda: "now",
        )

        self.assertEqual(health["overall_status"], "ok")
        self.assertEqual(health["checks"]["system"]["status"], "ok")
        self.assertEqual(health["checks"]["tailscale"]["status"], "ok")
        self.assertEqual(health["checks"]["voice"]["status"], "ok")

    def test_warning_behavior(self):
        health = health_status.get_health_status(
            system_reader=lambda: system_detail(memory=None),
            tailscale_reader=tailscale_detail,
            voice_reader=voice_detail,
            timestamp_reader=lambda: "now",
        )

        self.assertEqual(health["overall_status"], "warning")
        self.assertEqual(health["checks"]["system"]["status"], "warning")

    def test_error_behavior(self):
        health = health_status.get_health_status(
            system_reader=system_detail,
            tailscale_reader=lambda: tailscale_detail(ip=None),
            voice_reader=voice_detail,
            timestamp_reader=lambda: "now",
        )

        self.assertEqual(health["overall_status"], "error")
        self.assertEqual(health["checks"]["tailscale"]["status"], "error")

    def test_module_failure_does_not_crash_aggregator(self):
        def broken_reader():
            raise RuntimeError("boom")

        health = health_status.get_health_status(
            system_reader=system_detail,
            tailscale_reader=broken_reader,
            voice_reader=voice_detail,
            timestamp_reader=lambda: "now",
        )

        self.assertEqual(health["overall_status"], "error")
        self.assertEqual(health["checks"]["tailscale"]["status"], "error")
        self.assertIn("module failed", health["checks"]["tailscale"]["summary"])

    def test_summary_is_clean(self):
        health = health_status.get_health_status(
            system_reader=system_detail,
            tailscale_reader=tailscale_detail,
            voice_reader=voice_detail,
            timestamp_reader=lambda: "now",
        )

        summary = health_status.format_health_summary(health)

        self.assertIn("George 3 Health Status", summary)
        self.assertIn("Overall: OK", summary)
        self.assertIn("Tailscale: OK", summary)


if __name__ == "__main__":
    unittest.main()
