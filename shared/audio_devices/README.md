# Audio Devices

Metadata:
- Purpose: Shared audio device and Apple voice discovery.
- Phase: Architecture migration.
- Last updated: 2026-06-01.
- Notes: Read-only discovery; no recording, playback, transcription, or AI.

Purpose: discover microphones, output devices, and available Apple system
voices on this node.

The old CLI remains available during migration:

```bash
python3 -m modules.voice.voice_devices
```

New imports should prefer:

```python
from shared.audio_devices.voice_devices import discover_voice_devices
```

## Boundaries

This module only inspects local audio/voice configuration. It does not record,
play audio, transcribe, listen for wake words, identify speakers, call LLMs,
execute actions, or perform remote control.
