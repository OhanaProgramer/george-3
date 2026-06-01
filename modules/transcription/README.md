# Transcription Compatibility Wrapper

Metadata:
- Purpose: Preserve old transcription module path during architecture migration.
- Phase: Architecture migration.
- Last updated: 2026-06-01.
- Notes: Runtime implementation lives in `shared/speech_to_text/`.

The active transcription implementation has moved to:

```text
shared/speech_to_text/
```

The old CLI remains available during migration:

```bash
python3 -m modules.transcription.transcription data/voice_capture/latest_capture.wav
```

New imports should prefer:

```python
from shared.speech_to_text.transcription import transcribe_audio
```
