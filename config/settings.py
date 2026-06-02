"""George 3 configuration.

Purpose: Load local environment settings for modules.
Phase: Foundation configuration.
Last updated: 2026-05-31.
Notes: Does not store secrets or print `.env` contents.
"""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"


def load_env_file(env_file=ENV_FILE, override=True):
    """Load simple KEY=VALUE lines without printing or exposing secrets."""
    if not env_file.exists():
        return

    for raw_line in env_file.read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and (override or key not in os.environ):
            os.environ[key] = value


load_env_file()

GEORGE_NODE_NAME = os.getenv("GEORGE_NODE_NAME", "unknown-node")
GEORGE_NODE_ROLE = os.getenv("GEORGE_NODE_ROLE", "dev")
GEORGE_ENV = os.getenv("GEORGE_ENV", "development")
GEORGE_LOG_LEVEL = os.getenv("GEORGE_LOG_LEVEL", "info")

TAILSCALE_EXPECTED = os.getenv("TAILSCALE_EXPECTED", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
TAILSCALE_TIMEOUT_SECONDS = int(os.getenv("TAILSCALE_TIMEOUT_SECONDS", "5"))

BIND_ADDRESS = os.getenv("BIND_ADDRESS", "127.0.0.1")

VOICE_ENGINE = os.getenv("VOICE_ENGINE", "apple")
VOICE_NAME = os.getenv("VOICE_NAME", "")
VOICE_INPUT_DEVICE_HINT = os.getenv("VOICE_INPUT_DEVICE_HINT", "")
VOICE_OUTPUT_DEVICE_HINT = os.getenv("VOICE_OUTPUT_DEVICE_HINT", "system_default")
VOICE_PRODUCTION_SPEAKER_HINT = os.getenv("VOICE_PRODUCTION_SPEAKER_HINT", "")

TRANSCRIPTION_ENGINE = os.getenv("TRANSCRIPTION_ENGINE", "whisper_cli")
TRANSCRIPTION_COMMAND = os.getenv("TRANSCRIPTION_COMMAND", "whisper")
TRANSCRIPTION_MODEL = os.getenv("TRANSCRIPTION_MODEL", "base")
TRANSCRIPTION_LANGUAGE = os.getenv("TRANSCRIPTION_LANGUAGE", "en")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_FAST_MODEL = os.getenv("LLM_FAST_MODEL", "gpt-5.4-mini")
LLM_DEEP_MODEL = os.getenv("LLM_DEEP_MODEL", "gpt-5.5")
LLM_DEFAULT_TIER = os.getenv("LLM_DEFAULT_TIER", "fast")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def as_dict():
    return {
        "project_root": str(PROJECT_ROOT),
        "george_node_name": GEORGE_NODE_NAME,
        "george_node_role": GEORGE_NODE_ROLE,
        "george_env": GEORGE_ENV,
        "george_log_level": GEORGE_LOG_LEVEL,
        "tailscale_expected": TAILSCALE_EXPECTED,
        "tailscale_timeout_seconds": TAILSCALE_TIMEOUT_SECONDS,
        "bind_address": BIND_ADDRESS,
        "voice_engine": VOICE_ENGINE,
        "voice_name": VOICE_NAME,
        "voice_input_device_hint": VOICE_INPUT_DEVICE_HINT,
        "voice_output_device_hint": VOICE_OUTPUT_DEVICE_HINT,
        "voice_production_speaker_hint": VOICE_PRODUCTION_SPEAKER_HINT,
        "transcription_engine": TRANSCRIPTION_ENGINE,
        "transcription_command": TRANSCRIPTION_COMMAND,
        "transcription_model": TRANSCRIPTION_MODEL,
        "transcription_language": TRANSCRIPTION_LANGUAGE,
        "llm_provider": LLM_PROVIDER,
        "llm_fast_model": LLM_FAST_MODEL,
        "llm_deep_model": LLM_DEEP_MODEL,
        "llm_default_tier": LLM_DEFAULT_TIER,
        "openai_api_key_configured": bool(OPENAI_API_KEY),
    }


if __name__ == "__main__":
    for key, value in as_dict().items():
        print(f"{key}={value}")
