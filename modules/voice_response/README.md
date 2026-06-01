# Voice Response Compatibility Wrapper

Metadata:
- Purpose: Preserve old voice response module path during architecture migration.
- Phase: Architecture migration.
- Last updated: 2026-06-01.
- Notes: Runtime implementation lives in `interfaces/voice/response/`.

The active voice response implementation has moved to:

```text
interfaces/voice/response/
```

The old CLI remains available during migration:

```bash
python3 -m modules.voice_response.voice_response
```

New imports should prefer:

```python
from interfaces.voice.response.voice_response import run_voice_response
```
