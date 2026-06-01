"""Compatibility wrapper for the voice response interface.

Purpose: Preserve `python3 -m modules.voice_response.voice_response` during migration.
Phase: Architecture migration.
Last updated: 2026-06-01.
Notes: Runtime implementation lives in `interfaces.voice.response.voice_response`.
"""

from interfaces.voice.response.voice_response import *  # noqa: F401,F403
from interfaces.voice.response.voice_response import main


if __name__ == "__main__":
    main()
