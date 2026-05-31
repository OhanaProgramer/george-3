# Voice

Metadata:
- Purpose: Module overview for voice and audio discovery/speaking.
- Phase: Voice Speak v1.
- Last updated: 2026-05-31.
- Notes: Discovery plus Apple text-to-speech; no recording or transcription.

Purpose: discover available audio and Apple voice capability on this node, and
provide a small Apple text-to-speech smoke test.

Discovery is read-only for future dashboard/API use. Speaking is isolated in
`voice_speak.py` and only uses macOS `say`. The module does not record,
transcribe, identify speakers, listen for wake words, call AI, or control remote
systems.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.voice.voice_devices
```

```bash
python3 -m modules.voice.voice_speak "George voice test"
```

## Output

`voice_devices.py` returns a structured dictionary and prints a short terminal
summary.

The structured object is the useful part. The terminal summary is only for
learning and quick checks.

`voice_speak.py` returns a structured dictionary and prints it as JSON when run
from the CLI. It reads `VOICE_ENGINE` and `VOICE_NAME` from `.env` through
`config/settings.py`. When `VOICE_NAME` is blank, macOS uses the system default
voice.

## Inputs

- `VOICE_ENGINE`
- `VOICE_NAME`
- `VOICE_INPUT_DEVICE_HINT`
- `VOICE_OUTPUT_DEVICE_HINT`
- macOS audio and Apple voice discovery commands

## Boundaries

`voice_devices.py` does not record or play audio. `voice_speak.py` can speak
provided text with macOS `say`, but it does not record, transcribe, listen for
wake words, identify speakers, call AI, or execute actions.

## Future Relationships

`voice/` remains responsible for discovery and speech output. Recording belongs
in `voice_capture/`; audio-to-text belongs in `transcription/`.
