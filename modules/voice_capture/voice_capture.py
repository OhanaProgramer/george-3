"""Compatibility wrapper for the voice capture interface.

Purpose: Preserve `python3 -m modules.voice_capture.voice_capture` during migration.
Phase: Architecture migration.
Last updated: 2026-06-01.
Notes: Runtime implementation lives in `interfaces.voice.capture.voice_capture`.
"""

from interfaces.voice.capture.voice_capture import *  # noqa: F401,F403
from interfaces.voice.capture.voice_capture import main


if __name__ == "__main__":
    main()
