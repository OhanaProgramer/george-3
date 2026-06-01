# Voice

Metadata:
- Purpose: Document audio device discovery and Apple speech output.
- Phase: Voice Speak v1.
- Last updated: 2026-05-31.
- Notes: Discovery and speech output only; no recording or transcription.

Goal: discover available audio and Apple voice capability on this node, and
perform explicit Apple speech output when requested.

Device discovery is read-only. Speech output is isolated in
`shared.text_to_speech.voice_speak` and uses macOS `say`. The old
`modules.voice.voice_speak` CLI remains as a compatibility wrapper.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.voice.voice_devices
```

```bash
python3 -m modules.voice.voice_speak "George voice test"
```

## Test

```bash
python3 -m unittest tests.test_voice_devices tests.test_voice_speak
```

## What it checks

- available microphones
- available speakers/output devices when practical on macOS
- available Apple system voices
- whether the configured input hint is present
- whether the configured output hint is present
- whether the configured Apple voice is present, if `VOICE_NAME` is set

## What speaking checks

- `VOICE_ENGINE`
- `VOICE_NAME`
- explicit text provided by the caller

## Current boundaries

- recording is in `voice_capture/`
- audio-to-text is in `shared/speech_to_text/`
- text-to-speech is in `shared/text_to_speech/`
- wake word detection is future work
- speaker identification is future work
- conversation and intent logic are future work

## Future boundaries

- speaker identification will be separate
- wake word detection will be separate
- conversation and intent logic will be separate
