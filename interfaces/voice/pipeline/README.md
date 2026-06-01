# Voice Pipeline

Metadata:
- Purpose: Module overview for the manual one-shot voice pipeline.
- Phase: Voice Pipeline v1.
- Last updated: 2026-05-31.
- Notes: Manual capture -> transcription only; no wake word, speaker ID, LLM, or actions.

Purpose: answer whether George can record a short audio clip and transcribe it
in one command.

Manual voice pipeline v1:

```text
voice_capture
    |
    v
transcription
```

`modules/voice_pipeline/` remains as a compatibility wrapper during the
architecture migration. New code should import from `interfaces.voice.pipeline`.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.voice_pipeline.voice_pipeline
```

```bash
python3 -m modules.voice_pipeline.voice_pipeline --seconds 5
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

This module calls existing `interfaces/voice/capture/` and
`shared/speech_to_text/` modules. It
does not duplicate recording logic or transcription logic.

It does not listen continuously, detect wake words, identify speakers, call
LLMs, manage conversation memory, trigger actions, or perform remote control.
