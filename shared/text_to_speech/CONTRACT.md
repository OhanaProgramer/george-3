# Text To Speech Contract

Metadata:
- Purpose: Define shared text-to-speech boundaries.
- Phase: Architecture migration.
- Last updated: 2026-06-01.
- Notes: Apple `say` adapter only.

This module answers one question:

```text
Can George speak provided text using the configured local voice engine?
```

## Allowed

- read voice settings from `config/settings.py`
- call macOS `say`
- use `VOICE_NAME` when set
- use the system default Apple voice when `VOICE_NAME` is blank
- return a structured speech result object

## Not Allowed

- recording
- transcription
- wake-word detection
- speaker identification
- LLM calls
- action execution
- remote control
