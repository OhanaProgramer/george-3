# Voice Capture Module Contract

Metadata:
- Purpose: Define one-shot voice capture boundaries.
- Phase: Voice Capture v1.
- Last updated: 2026-05-31.
- Notes: Short recording only; not an always-on listener.

This module answers one question:

```text
Can George successfully capture audio from the configured microphone?
```

## Allowed in v1

- read `VOICE_INPUT_DEVICE_HINT`
- read `GEORGE_ENV`
- inspect voice device discovery data
- perform one short audio capture
- write `data/voice_capture/latest_capture.wav`
- return a structured result object
- print a clean terminal summary

## Inputs

- `VOICE_INPUT_DEVICE_HINT` from `config/settings.py`
- `GEORGE_ENV` from `config/settings.py`
- voice device discovery data
- requested capture duration

## Outputs

- structured capture result object
- WAV file at `data/voice_capture/latest_capture.wav`

## Not Allowed in v1

- continuous audio monitoring
- wake-word detection
- transcription
- speaker identification
- OpenAI calls
- automation
- remote control

Voice Capture v1 is a small building block for future voice functionality. A
future `wake_listener/` module may reuse it, but this module itself records once
and exits.
