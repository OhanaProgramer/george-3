"""Compatibility wrapper for the shared text-to-speech module.

Purpose: Preserve `python3 -m modules.voice.voice_speak` during migration.
Phase: Architecture migration.
Last updated: 2026-06-01.
Notes: Runtime implementation lives in `shared.text_to_speech.voice_speak`.
"""

from shared.text_to_speech.voice_speak import *  # noqa: F401,F403
from shared.text_to_speech.voice_speak import main


if __name__ == "__main__":
    main()
