# Voice Capture

Metadata:
- Purpose: Module overview for one-shot audio capture.
- Phase: Voice Capture v1.
- Last updated: 2026-05-31.
- Notes: One capture and exit; no wake word, transcription, speaker ID, or AI.

Purpose: answer whether George can successfully capture audio from the
configured microphone.

This module performs one short recording and exits. It reads
`VOICE_INPUT_DEVICE_HINT` and `GEORGE_ENV` from `config/settings.py`, uses voice
device discovery to find the configured microphone, and writes a WAV file to:

```text
data/voice_capture/latest_capture.wav
```

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.voice_capture.voice_capture
```

```bash
python3 -m modules.voice_capture.voice_capture --seconds 5
```

## Product

The structured result object is the product. Terminal output is display only.

Voice Capture v1 does not continuously monitor audio, detect wake words,
transcribe, identify speakers, call OpenAI, perform automation, or control
remote systems.
