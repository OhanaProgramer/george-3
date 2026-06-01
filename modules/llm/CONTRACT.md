# LLM Adapter Module Contract

Metadata:
- Purpose: Define text-to-LLM response boundaries.
- Phase: LLM Adapter v1.
- Last updated: 2026-05-31.
- Notes: Text in, text out only.

This module answers one question:

```text
Can George send text to the configured LLM provider and receive a text response?
```

## Allowed in v1

- read LLM configuration from `config/settings.py`
- send provided text to the configured provider
- use the configured fast or deep model tier
- return a structured result object
- print readable terminal output
- exit

## Inputs

- input text
- `LLM_PROVIDER`
- `LLM_FAST_MODEL`
- `LLM_DEEP_MODEL`
- `LLM_DEFAULT_TIER`
- `OPENAI_API_KEY`

## Outputs

- structured LLM result object
- provider response text when successful

## Not Allowed in v1

- audio capture
- transcription
- speech output
- command routing
- action execution
- remote control
- conversation memory
- deciding whether input should go to the LLM

Future input routing should be separate from this adapter.
