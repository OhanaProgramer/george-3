# Voice Assistant Compatibility Wrapper

Metadata:
- Purpose: Preserve old voice assistant module path during architecture migration.
- Phase: Architecture migration.
- Last updated: 2026-06-01.
- Notes: Runtime implementation lives in `interfaces/voice/assistant/`.

The active voice assistant implementation has moved to:

```text
interfaces/voice/assistant/
```

The old CLI remains available during migration:

```bash
python3 -m modules.voice_assistant.voice_assistant
```

New imports should prefer:

```python
from interfaces.voice.assistant.voice_assistant import run_voice_assistant
```
