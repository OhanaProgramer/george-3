"""System status tests.

Purpose: Verify local system status object shape and safe optional data handling.
Phase: System Discovery v1.
Last updated: 2026-05-31.
Notes: Uses injected readers where practical to avoid machine-specific failures.
"""

import unittest

from config import settings
from modules.system import system_status


class SystemStatusTests(unittest.TestCase):
    def test_object_shape(self):
        status = system_status.get_system_status(
            memory_reader=lambda: 16.0,
            disk_reader=lambda: (500.0, 250.0),
            cpu_reader=lambda: 8,
            cwd_reader=lambda: "/tmp/george-3",
            timestamp_reader=lambda: "2026-05-30T00:00:00+00:00",
        )

        self.assertEqual(set(status.keys()), {"node", "host", "resources", "paths", "timestamp"})
        self.assertEqual(
            set(status["node"].keys()),
            {"name", "role", "environment", "log_level"},
        )
        self.assertEqual(
            set(status["host"].keys()),
            {"hostname", "os", "os_version", "architecture", "python_version"},
        )
        self.assertEqual(
            set(status["resources"].keys()),
            {"cpu_count", "memory_total_gb", "disk_total_gb", "disk_free_gb"},
        )
        self.assertEqual(set(status["paths"].keys()), {"cwd", "project_root"})

    def test_config_values_are_included(self):
        status = system_status.get_system_status(
            memory_reader=lambda: None,
            disk_reader=lambda: (None, None),
            cpu_reader=lambda: 1,
            cwd_reader=lambda: "/tmp/george-3",
            timestamp_reader=lambda: "now",
        )

        self.assertEqual(status["node"]["name"], settings.GEORGE_NODE_NAME)
        self.assertEqual(status["node"]["role"], settings.GEORGE_NODE_ROLE)
        self.assertEqual(status["node"]["environment"], settings.GEORGE_ENV)
        self.assertEqual(status["node"]["log_level"], settings.GEORGE_LOG_LEVEL)

    def test_missing_optional_resource_data_does_not_crash(self):
        status = system_status.get_system_status(
            memory_reader=lambda: None,
            disk_reader=lambda: None,
            cpu_reader=lambda: None,
            cwd_reader=lambda: "/tmp/george-3",
            timestamp_reader=lambda: "now",
        )

        self.assertEqual(status["resources"]["cpu_count"], 0)
        self.assertIsNone(status["resources"]["memory_total_gb"])
        self.assertIsNone(status["resources"]["disk_total_gb"])
        self.assertIsNone(status["resources"]["disk_free_gb"])

    def test_core_fields_are_present(self):
        status = system_status.get_system_status()

        self.assertTrue(status["host"]["hostname"])
        self.assertTrue(status["host"]["os"])
        self.assertTrue(status["host"]["python_version"])
        self.assertTrue(status["paths"]["cwd"])
        self.assertTrue(status["paths"]["project_root"])
        self.assertTrue(status["timestamp"])

    def test_summary_is_readable(self):
        status = system_status.get_system_status(
            memory_reader=lambda: None,
            disk_reader=lambda: (100.0, 50.0),
            cpu_reader=lambda: 4,
            cwd_reader=lambda: "/tmp/george-3",
            timestamp_reader=lambda: "now",
        )

        summary = system_status.format_system_summary(status)

        self.assertIn("George 3 System Status", summary)
        self.assertIn("CPU count: 4", summary)
        self.assertIn("Disk free GB: 50.0", summary)


if __name__ == "__main__":
    unittest.main()
