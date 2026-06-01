# Push-To-Talk Compatibility Wrapper

Metadata:
- Purpose: Preserve old push-to-talk module path during architecture migration.
- Phase: Architecture migration.
- Last updated: 2026-06-01.
- Notes: Runtime implementation lives in `interfaces/voice/push_to_talk/`.

The active push-to-talk implementation has moved to:

```text
interfaces/voice/push_to_talk/
```

The old CLI remains available during migration:

```bash
python3 -m modules.push_to_talk.push_to_talk
```

New imports should prefer:

```python
from interfaces.voice.push_to_talk.push_to_talk import run_push_to_talk
```
