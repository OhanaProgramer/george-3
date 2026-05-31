"""Tailscale status tests.

Purpose: Verify local Tailscale status parsing and display behavior.
Phase: Tailscale Discovery v1.
Last updated: 2026-05-31.
Notes: Uses fake command output; does not require live Tailscale.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.tailscale import tailscale_status


def make_result(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


class TailscaleStatusTests(unittest.TestCase):
    def test_not_installed_is_not_ok_when_expected(self):
        with patch.object(tailscale_status, "is_tailscale_installed", return_value=False):
            status = tailscale_status.get_tailscale_status()

        self.assertFalse(status["installed"])
        self.assertFalse(status["running"])
        self.assertEqual(status["message"], "Tailscale is not installed.")

    def test_running_status_reads_ip(self):
        with patch.object(tailscale_status, "is_tailscale_installed", return_value=True):

            def fake_runner(command):
                if command == ["tailscale", "status", "--json"]:
                    return make_result(stdout='{"BackendState": "Running"}')
                if command == ["tailscale", "ip", "-4"]:
                    return make_result(stdout="100.64.1.2\n")
                raise AssertionError(f"Unexpected command: {command}")

            status = tailscale_status.get_tailscale_status(fake_runner)

        self.assertTrue(status["installed"])
        self.assertTrue(status["running"])
        self.assertEqual(status["backend_state"], "Running")
        self.assertEqual(status["tailscale_ip"], "100.64.1.2")

    def test_summary_is_readable(self):
        summary = tailscale_status.format_status_summary(
            {
                "node_name": "macpro-dev",
                "node_role": "dev",
                "tailscale_expected": True,
                "installed": True,
                "running": True,
                "backend_state": "Running",
                "tailscale_ip": "100.64.1.2",
                "ok": True,
                "message": "Tailscale is running.",
            }
        )

        self.assertIn("George 3 Tailscale Status", summary)
        self.assertIn("Node: macpro-dev (dev)", summary)
        self.assertIn("Tailscale IP: 100.64.1.2", summary)


if __name__ == "__main__":
    unittest.main()
