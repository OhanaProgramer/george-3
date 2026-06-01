# Transcription Module Contract

Metadata:
- Purpose: Define audio-to-text transcription boundaries.
- Phase: Transcription v1.
- Last updated: 2026-05-31.
- Notes: Existing audio file to text only.

This module answers one question:

```text
Can George convert recorded speech into text?
```

## Allowed in v1

- read an existing WAV file
- read transcription settings from `config/settings.py`
- call a local transcription engine
- produce transcript text
- return a structured result object
- print a clean terminal summary

## Inputs

- existing audio file
- `TRANSCRIPTION_ENGINE`
- `TRANSCRIPTION_COMMAND`
- `TRANSCRIPTION_MODEL`
- `TRANSCRIPTION_LANGUAGE`

## Outputs

- structured transcription result object
- transcript text

## Not Allowed in v1

- wake-word detection
- speaker identification
- conversation logic
- continuous listening
- microphone monitoring
- OpenAI calls
- action execution
- automation triggers

Transcription must remain independent. It should be possible to replace Whisper
with a future transcription engine without changing `speaker_id/`,
`conversation/`, or `actions/`.
