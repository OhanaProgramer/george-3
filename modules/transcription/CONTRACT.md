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
- call a local transcription engine
- produce transcript text
- return a structured result object
- print a clean terminal summary

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
