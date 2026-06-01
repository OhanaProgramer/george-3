# Push-To-Talk

Metadata:
- Purpose: Module overview for user-controlled recording and transcription.
- Phase: Push-To-Talk v1.
- Last updated: 2026-05-31.
- Notes: Manual start/stop only; no wake word, speaker ID, LLM, actions, or speech response.

Purpose: answer whether a user can manually start recording, manually stop
recording, and obtain a transcript.

Current interaction path:

```text
push_to_talk
    |
    v
voice_capture
    |
    v
transcription
```

Push-To-Talk v1 is a learning and integration module. It orchestrates existing
capture and transcription modules; it does not own recording or transcription
logic.

`modules/push_to_talk/` remains as a compatibility wrapper during the
architecture migration. New code should import from
`interfaces.voice.push_to_talk`.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.push_to_talk.push_to_talk
```

## Product

The structured result object is the product. Terminal output is display only.

Structured result:

```text
{
  "success": true/false,
  "capture": {},
  "transcription": {},
  "transcript": "",
  "message": "",
  "error": ""
}
```

## Boundaries

This module does not continuously listen, detect wake words, identify speakers,
call LLMs, maintain conversation memory, perform actions, perform remote
control, or speak responses.

## Future Roadmap

Planned sequence after Push-To-Talk v1:

1. LLM Adapter: text -> AI response
2. Voice Response Pipeline: capture -> transcription -> LLM -> voice_speak
3. Wake Listener: always-on monitoring, wake phrase detection, automatic trigger
   of the existing pipeline

Those future steps are not implemented here.
