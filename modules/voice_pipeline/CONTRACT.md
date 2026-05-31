# Voice Pipeline Module Contract

Metadata:
- Purpose: Define manual one-shot voice pipeline boundaries.
- Phase: Voice Pipeline v1.
- Last updated: 2026-05-31.
- Notes: Manual capture -> transcription only.

This module answers one question:

```text
Can George record a short audio clip and transcribe it in one command?
```

## Allowed in v1

- call the existing voice capture module
- call the existing transcription module
- return a structured result object
- print a readable terminal summary
- exit

## Inputs

- capture duration
- voice capture result
- transcription result

## Outputs

- structured pipeline result object
- transcript text when transcription succeeds

## Not Allowed in v1

- continuous listening
- wake-word detection
- speaker identification
- LLM calls
- conversation memory
- action execution
- remote control

Terminal output is display only. The structured result object is the module
product.
