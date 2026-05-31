# Push-To-Talk Module Contract

Metadata:
- Purpose: Define user-triggered recording and transcription boundaries.
- Phase: Push-To-Talk v1.
- Last updated: 2026-05-31.
- Notes: Manual start/stop only.

This module answers one question:

```text
Can a user manually start recording, manually stop recording, and obtain a transcript?
```

## Allowed in v1

- wait for the user to press ENTER to start recording
- start recording through `voice_capture`
- wait for the user to press ENTER to stop recording
- stop recording through `voice_capture`
- transcribe the captured WAV through `transcription`
- return a structured result object
- print readable terminal output
- exit

## Inputs

- user ENTER keypresses
- voice capture result
- transcription result

## Outputs

- structured push-to-talk result object
- transcript text when transcription succeeds

## Not Allowed in v1

- continuous listening
- wake-word detection
- speaker identification
- LLM calls
- conversation memory
- action execution
- remote control
- spoken responses

Terminal output is display only. The structured result object is the module
product.
