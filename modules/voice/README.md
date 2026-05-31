# Voice

Metadata:
- Purpose: Module overview for voice and audio discovery.
- Phase: Voice Discovery v1.
- Last updated: 2026-05-31.
- Notes: Discovery only; no recording, playback, or transcription.

Purpose: discover available audio and Apple voice capability on this node.

This is read-only discovery for future dashboard/API use. It does not record,
play audio, speak, transcribe, identify speakers, listen for wake words, call AI,
or control remote systems.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.voice.voice_devices
```

## Output

`voice_devices.py` returns a structured dictionary and prints a short terminal
summary.

The structured object is the useful part. The terminal summary is only for
learning and quick checks.
