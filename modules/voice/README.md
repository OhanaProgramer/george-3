# Voice

Metadata:
- Purpose: Module overview for voice and audio discovery/speaking.
- Phase: Voice Speak v1.
- Last updated: 2026-05-31.
- Notes: Discovery plus Apple text-to-speech; no recording or transcription.

Purpose: preserve voice discovery and speech CLIs while implementation moves
into shared service namespaces.

Discovery now lives in `shared/audio_devices/voice_devices.py`. Speaking now
lives in `shared/text_to_speech/voice_speak.py` and only uses macOS `say`. The
old `modules.voice` paths remain as compatibility wrappers. The module does not
record, transcribe, identify speakers, listen for wake words, call AI, or
control remote systems.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.voice.voice_devices
```

```bash
python3 -m modules.voice.voice_speak "George voice test"
```

## Output

`shared/audio_devices/voice_devices.py` returns a structured dictionary and
prints a short terminal summary.

The structured object is the useful part. The terminal summary is only for
learning and quick checks.

`shared/text_to_speech/voice_speak.py` returns a structured dictionary and
prints it as JSON when run from the CLI. It reads `VOICE_ENGINE` and
`VOICE_NAME` from `.env` through `config/settings.py`. When `VOICE_NAME` is
blank, macOS uses the system default voice.

## Inputs

- `VOICE_ENGINE`
- `VOICE_NAME`
- `VOICE_INPUT_DEVICE_HINT`
- `VOICE_OUTPUT_DEVICE_HINT`
- macOS audio and Apple voice discovery commands

## Boundaries

`voice_devices.py` does not record or play audio. `voice_speak.py` can speak
provided text with macOS `say`, but it does not record, transcribe, listen for
wake words, identify speakers, call AI, or execute actions.

## Future Relationships

`voice/` is currently a compatibility namespace. Discovery lives in
`shared/audio_devices/`, speech output lives in `shared/text_to_speech/`,
recording belongs in `interfaces/voice/capture/`, and audio-to-text belongs in
`shared/speech_to_text/`.
