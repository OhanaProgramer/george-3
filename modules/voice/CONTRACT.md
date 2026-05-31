# Voice Module Contract

This module answers one question:

```text
What voice/audio devices and Apple voices are available on this node?
```

## Allowed in Phase 1

- discover microphones
- discover speakers/output devices when practical
- discover Apple system voices when practical
- normalize discovery into structured data
- check configured hints from `.env`
- print a clean summary

## Not Allowed in Phase 1

- recording
- playback
- speaking
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
