"""Settings tests.

Purpose: Verify project .env precedence.
Phase: Environment precedence verification.
Last updated: 2026-05-31.
Notes: Uses temporary env files and fake keys; does not expose secrets.
"""

import os
import tempfile
import unittest
from pathlib import Path

from config import settings


class SettingsTests(unittest.TestCase):
    def test_load_env_file_overrides_existing_shell_value_by_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("OPENAI_API_KEY=project-value\n")
            old_value = os.environ.get("OPENAI_API_KEY")
            os.environ["OPENAI_API_KEY"] = "shell-value"

            try:
                settings.load_env_file(env_file)
                self.assertEqual(os.environ["OPENAI_API_KEY"], "project-value")
            finally:
                if old_value is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = old_value

    def test_load_env_file_can_preserve_shell_value_when_requested(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("OPENAI_API_KEY=project-value\n")
            old_value = os.environ.get("OPENAI_API_KEY")
            os.environ["OPENAI_API_KEY"] = "shell-value"

            try:
                settings.load_env_file(env_file, override=False)
                self.assertEqual(os.environ["OPENAI_API_KEY"], "shell-value")
            finally:
                if old_value is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = old_value


if __name__ == "__main__":
    unittest.main()
