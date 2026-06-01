"""Compatibility wrapper for the voice assistant interface.

Purpose: Preserve `python3 -m modules.voice_assistant.voice_assistant` during migration.
Phase: Architecture migration.
Last updated: 2026-06-01.
Notes: Runtime implementation lives in `interfaces.voice.assistant.voice_assistant`.
"""

from interfaces.voice.assistant.voice_assistant import *  # noqa: F401,F403
from interfaces.voice.assistant.voice_assistant import main


if __name__ == "__main__":
    main()
