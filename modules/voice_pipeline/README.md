# Voice Pipeline Compatibility Wrapper

Metadata:
- Purpose: Preserve old voice pipeline module path during architecture migration.
- Phase: Architecture migration.
- Last updated: 2026-06-01.
- Notes: Runtime implementation lives in `interfaces/voice/pipeline/`.

The active voice pipeline implementation has moved to:

```text
interfaces/voice/pipeline/
```

The old CLI remains available during migration:

```bash
python3 -m modules.voice_pipeline.voice_pipeline --seconds 5
```

New imports should prefer:

```python
from interfaces.voice.pipeline.voice_pipeline import run_voice_pipeline
```
