"""Prove George config uses project .env precedence.

Purpose: Compare raw project .env value with config/settings.py value.
Phase: Environment precedence verification.
Last updated: 2026-05-31.
Notes: Masks secret values; does not print full API keys.
"""

from __future__ import annotations

from config import settings


def read_env_value(key, env_file=settings.ENV_FILE):
    if not env_file.exists():
        return ""

    for raw_line in env_file.read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        raw_key, raw_value = line.split("=", 1)

        if raw_key.strip() == key:
            return raw_value.strip().strip('"').strip("'")

    return ""


def mask_secret(value):
    if not value:
        return "(empty)"

    if len(value) <= 12:
        return "*" * len(value)

    return f"{value[:8]}...{value[-4:]}"


def main():
    raw_key = read_env_value("OPENAI_API_KEY")
    settings_key = settings.OPENAI_API_KEY

    print("=== GEORGE ENV PRECEDENCE ===")
    print(f"Project .env : {settings.ENV_FILE}")
    print(f"Raw .env     : {mask_secret(raw_key)}")
    print(f"Settings     : {mask_secret(settings_key)}")
    print(f"MATCH        : {raw_key == settings_key}")


if __name__ == "__main__":
    main()
