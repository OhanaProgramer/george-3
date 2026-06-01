"""Compatibility wrapper for the manual voice pipeline interface.

Purpose: Preserve `python3 -m modules.voice_pipeline.voice_pipeline` during migration.
Phase: Architecture migration.
Last updated: 2026-06-01.
Notes: Runtime implementation lives in `interfaces.voice.pipeline.voice_pipeline`.
"""

from interfaces.voice.pipeline.voice_pipeline import *  # noqa: F401,F403
from interfaces.voice.pipeline.voice_pipeline import main


if __name__ == "__main__":
    main()
