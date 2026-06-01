"""Compatibility wrapper for the shared speech-to-text transcription module.

Purpose: Preserve `python3 -m modules.transcription.transcription` during migration.
Phase: Architecture migration.
Last updated: 2026-06-01.
Notes: Runtime implementation lives in `shared.speech_to_text.transcription`.
"""

from shared.speech_to_text.transcription import *  # noqa: F401,F403
from shared.speech_to_text.transcription import main


if __name__ == "__main__":
    main()
