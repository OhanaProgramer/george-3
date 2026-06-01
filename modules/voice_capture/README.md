# Voice Capture Compatibility Wrapper

Metadata:
- Purpose: Preserve old voice capture module path during architecture migration.
- Phase: Architecture migration.
- Last updated: 2026-06-01.
- Notes: Runtime implementation lives in `interfaces/voice/capture/`.

The active voice capture implementation has moved to:

```text
interfaces/voice/capture/
```

The old CLI remains available during migration:

```bash
python3 -m modules.voice_capture.voice_capture --seconds 3
```

New imports should prefer:

```python
from interfaces.voice.capture.voice_capture import capture_audio
```
