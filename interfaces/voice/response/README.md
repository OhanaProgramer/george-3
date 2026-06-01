# Voice Response

Metadata:
- Purpose: Module overview for simple transcript-to-speech response.
- Phase: Voice Response v1.
- Last updated: 2026-05-31.
- Notes: No LLM, wake word, speaker ID, conversation memory, actions, or remote control.

Purpose: prove George can hear a manually triggered utterance and speak back a
simple confirmation.

Voice Response v1:

```text
push_to_talk
    |
    v
voice_speak
```

The spoken response is intentionally simple:

```text
I heard: <transcript>
```

`modules/voice_response/` remains as a compatibility wrapper during the
architecture migration. New code should import from `interfaces.voice.response`.

## Run

From `~/Projects/george-3` in an environment where Whisper is available:

```bash
python3 -m modules.voice_response.voice_response
```

## Product

The structured result object is the product. Terminal output is display only.

Structured result:

```text
{
  "success": true/false,
  "push_to_talk": {},
  "spoken_response": {},
  "transcript": "",
  "response_text": "",
  "message": "",
  "error": ""
}
```

## Boundaries

This module does not call an LLM, detect wake words, identify speakers, maintain
conversation memory, execute actions, perform remote control, or choose an
intelligent response. It only confirms what was transcribed.

## Future Roadmap

The future LLM adapter can replace the fixed confirmation response with a model
response while preserving the capture/transcription/speech boundaries.
