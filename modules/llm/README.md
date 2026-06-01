# LLM

Metadata:
- Purpose: Module overview for AI model adapter.
- Phase: LLM Adapter v1.
- Last updated: 2026-05-31.
- Notes: Text in, text out; no audio, routing, actions, or memory.

Purpose: answer whether George can send text to the configured LLM provider and
receive a text response.

Current provider: OpenAI.

Current design: the Mini Mac or MacBook handles local audio. OpenAI handles
reasoning.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.llm.llm_adapter "Hello George"
```

```bash
python3 -m modules.llm.llm_adapter "Explain gravity simply" --tier deep
```

## Configuration

The adapter reads:

- `LLM_PROVIDER`
- `LLM_FAST_MODEL`
- `LLM_DEEP_MODEL`
- `LLM_DEFAULT_TIER`
- `OPENAI_API_KEY`

The current supported provider is `openai`. The current implementation uses the
OpenAI Responses API through the OpenAI Python SDK.

## Product

The structured result object is the product. Terminal output is display only.

Structured result:

```text
{
  "success": true/false,
  "provider": "openai",
  "model": "",
  "tier": "fast",
  "input_text": "",
  "response_text": "",
  "message": "",
  "error": ""
}
```

## Boundaries

This module does not capture audio, transcribe audio, speak responses, route
commands, execute actions, perform remote control, maintain conversation memory,
or decide whether input should go to the LLM.

Future routing should live in a separate `input_router/` module.
