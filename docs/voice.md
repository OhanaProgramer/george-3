# Voice Discovery

Metadata:
- Purpose: Document audio device and Apple voice discovery.
- Phase: Voice Discovery v1.
- Last updated: 2026-05-31.
- Notes: Discovery only; no recording, playback, or transcription.

Goal: discover available audio and Apple voice capability on this node.

This is read-only discovery only.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.voice.voice_devices
```

## Test

```bash
python3 -m unittest tests.test_voice_devices
```

## What it checks

- available microphones
- available speakers/output devices when practical on macOS
- available Apple system voices
- whether the configured input hint is present
- whether the configured output hint is present
- whether the configured Apple voice is present, if `VOICE_NAME` is set

## Future boundaries

- voice capture will be separate
- transcription will be separate
- speaker identification will be separate
- wake word detection will be separate
- conversation and intent logic will be separate
