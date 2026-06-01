# Voice Assistant

Metadata:
- Purpose: Module overview for the first hear-think-speak conversational loop.
- Phase: Voice Assistant v1.
- Last updated: 2026-05-31.
- Notes: Orchestration only; no wake word, memory, tools, actions, or remote control.

Purpose: answer whether George can hear a spoken request, think using the
configured LLM, and speak the response.

Current conversational path:

```text
push_to_talk
    |
    v
transcription
    |
    v
llm_adapter
    |
    v
voice_speak
```

## Run

From `~/Projects/george-3` in an environment where Whisper, OpenAI SDK, and the
project `.env` are available:

```bash
python3 -m modules.voice_assistant.voice_assistant
```

## Product

The structured result object is the product. Terminal output is display only.

Structured result:

```text
{
  "success": true/false,
  "transcript": "",
  "llm_response": "",
  "capture": {},
  "transcription": {},
  "llm": {},
  "speech": {},
  "message": "",
  "error": ""
}
```

## Boundaries

This module does not continuously listen, detect wake words, identify speakers,
maintain conversation memory, execute actions, perform remote control, call
tools, or control devices.

It is hear -> think -> speak only.

## Future Path

Future work may insert:

```text
wake_listener
    |
    v
transcription
    |
    v
input_router
    |
    v
llm_adapter
    |
    v
voice_speak
```

Those future modules are not implemented here.
