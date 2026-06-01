"""Compatibility wrapper for shared audio device discovery.

Purpose: Preserve `python3 -m modules.voice.voice_devices` during migration.
Phase: Architecture migration.
Last updated: 2026-06-01.
Notes: Runtime implementation lives in `shared.audio_devices.voice_devices`.
"""

from shared.audio_devices.voice_devices import *  # noqa: F401,F403
from shared.audio_devices.voice_devices import main


if __name__ == "__main__":
    main()
