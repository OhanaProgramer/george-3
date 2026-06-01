# Text To Speech

Metadata:
- Purpose: Shared text-to-speech service module.
- Phase: Architecture migration.
- Last updated: 2026-06-01.
- Notes: Apple `say` adapter only; no recording, transcription, wake word, or AI.

Purpose: speak provided text using the configured local speech engine.

The current supported engine is Apple text-to-speech through macOS `say`.
Settings come from `config/settings.py`:

- `VOICE_ENGINE`
- `VOICE_NAME`

The old CLI remains available during migration:

```bash
python3 -m modules.voice.voice_speak "George voice test"
```

New imports should prefer:

```python
from shared.text_to_speech.voice_speak import speak_text
```

## Product

The structured result object is the product. Terminal output is display only.

## Boundaries

This module does not record audio, transcribe audio, listen for wake words,
identify speakers, call LLMs, execute actions, or perform remote control.
