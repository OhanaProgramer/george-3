"""Compatibility wrapper for the push-to-talk voice interface.

Purpose: Preserve `python3 -m modules.push_to_talk.push_to_talk` during migration.
Phase: Architecture migration.
Last updated: 2026-06-01.
Notes: Runtime implementation lives in `interfaces.voice.push_to_talk.push_to_talk`.
"""

from interfaces.voice.push_to_talk.push_to_talk import *  # noqa: F401,F403
from interfaces.voice.push_to_talk.push_to_talk import main


if __name__ == "__main__":
    main()
