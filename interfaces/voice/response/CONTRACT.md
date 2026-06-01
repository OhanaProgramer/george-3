# Voice Response Module Contract

Metadata:
- Purpose: Define simple transcript-to-speech response boundaries.
- Phase: Voice Response v1.
- Last updated: 2026-05-31.
- Notes: Confirmation response only; no LLM.

This module answers one question:

```text
Can George hear a manually triggered utterance and speak back a simple confirmation?
```

## Allowed in v1

- call the existing push-to-talk module
- build a fixed confirmation response from the transcript
- call the existing voice speak module
- return a structured result object
- print readable terminal output
- exit

## Inputs

- push-to-talk result
- transcript text
- voice speak result

## Outputs

- structured voice response result object
- spoken confirmation when speech output succeeds

## Not Allowed in v1

- LLM calls
- wake-word detection
- speaker identification
- conversation memory
- action execution
- remote control
- response reasoning

Terminal output is display only. The structured result object is the module
product.
