import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.tailscale import tailnet_nodes


def make_result(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


class TailnetNodesTests(unittest.TestCase):
    def test_inventory_normalizes_self_and_peers(self):
        raw_status = {
            "BackendState": "Running",
            "CurrentTailnet": {"Name": "example.ts.net"},
            "Self": {
                "HostName": "macpro-dev",
                "DNSName": "macpro-dev.example.ts.net.",
                "OS": "macOS",
                "TailscaleIPs": ["100.64.1.2"],
                "Online": True,
                "Active": True,
            },
            "Peer": {
                "nodekey:abc": {
                    "HostName": "minimac-home",
                    "DNSName": "minimac-home.example.ts.net.",
                    "OS": "macOS",
                    "TailscaleIPs": ["100.64.1.3"],
                    "Online": False,
                    "Active": False,
                    "LastSeen": "2026-05-30T18:00:00Z",
                }
            },
        }

        inventory = tailnet_nodes.build_tailnet_inventory(raw_status)

        self.assertTrue(inventory["ok"])
        self.assertEqual(inventory["node_count"], 2)
        self.assertEqual(inventory["online_count"], 1)
        self.assertEqual(inventory["offline_count"], 1)
        self.assertTrue(inventory["nodes"][0]["is_self"])
        self.assertEqual(inventory["nodes"][1]["name"], "minimac-home")

    def test_load_tailnet_status_handles_missing_tailscale(self):
        with patch.object(tailnet_nodes, "is_tailscale_installed", return_value=False):
            inventory = tailnet_nodes.load_tailnet_status()

        self.assertFalse(inventory["ok"])
        self.assertEqual(inventory["nodes"], [])

    def test_load_tailnet_status_uses_command_runner(self):
        with patch.object(tailnet_nodes, "is_tailscale_installed", return_value=True):

            def fake_runner(command):
                self.assertEqual(command, ["tailscale", "status", "--json"])
                return make_result(
                    stdout='{"BackendState":"Running","Self":{"HostName":"macpro-dev","TailscaleIPs":["100.64.1.2"],"Online":true},"Peer":{}}'
                )

            inventory = tailnet_nodes.load_tailnet_status(fake_runner)

        self.assertTrue(inventory["ok"])
        self.assertEqual(inventory["self"]["primary_ip"], "100.64.1.2")

    def test_summary_is_dashboard_readable(self):
        inventory = {
            "ok": True,
            "message": "loaded",
            "backend_state": "Running",
            "tailnet": "example.ts.net",
            "node_count": 1,
            "online_count": 1,
            "offline_count": 0,
            "nodes": [
                {
                    "name": "macpro-dev",
                    "primary_ip": "100.64.1.2",
                    "os": "macOS",
                    "online": True,
                    "is_self": True,
                }
            ],
        }

        summary = tailnet_nodes.format_tailnet_summary(inventory)

        self.assertIn("George 3 Tailnet Nodes", summary)
        self.assertIn("1 total, 1 online, 0 offline", summary)
        self.assertIn("macpro-dev", summary)


if __name__ == "__main__":
    unittest.main()
