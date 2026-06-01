# Voice Assistant Module Contract

Metadata:
- Purpose: Define hear-think-speak orchestration boundaries.
- Phase: Voice Assistant v1.
- Last updated: 2026-05-31.
- Notes: Orchestration only.

This module answers one question:

```text
Can George hear a spoken request, think using the configured LLM, and speak the response?
```

## Allowed in v1

- call the existing push-to-talk module
- pass the transcript to the existing LLM adapter
- pass the LLM response text to the existing voice speak module
- return a structured result object
- print readable terminal output
- exit

## Inputs

- push-to-talk result
- transcript text
- LLM result
- speech result

## Outputs

- structured voice assistant result object
- transcript text
- LLM response text
- spoken response when speech succeeds

## Not Allowed in v1

- continuous listening
- wake-word detection
- speaker identification
- conversation memory
- action execution
- remote control
- tool calls
- device control

Terminal output is display only. The structured result object is the module
product.
