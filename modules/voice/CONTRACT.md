# Voice Module Contract

Metadata:
- Purpose: Define voice module boundaries.
- Phase: Voice Speak v1.
- Last updated: 2026-05-31.
- Notes: Device/voice discovery plus isolated Apple text-to-speech.

This module answers two questions:

```text
What voice/audio devices and Apple voices are available on this node?
Can this node speak a simple test phrase using macOS say?
```

## Allowed

- discover microphones
- discover speakers/output devices when practical
- discover Apple system voices when practical
- normalize discovery into structured data
- check configured hints from `.env`
- print a clean summary
- speak provided text with macOS `say`
- use `VOICE_NAME` when set
- use the system default Apple voice when `VOICE_NAME` is blank

## Inputs

- voice settings from `config/settings.py`
- macOS audio device discovery
- macOS Apple voice discovery
- provided text for explicit speech tests

## Outputs

- structured voice discovery object
- structured speech result object
- terminal summaries for humans

## Not Allowed

- recording
- Whisper
- transcription
- speaker identification
- wake word
- AI calls
- remote control

## Future Separate Modules

- voice capture will be separate
- transcription will be separate
- speaker identification will be separate
- wake word detection will be separate
- conversation and intent logic will be separate

Future capture and transcription modules consume their own inputs. They should
not be folded into `voice/`.
