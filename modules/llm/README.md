# LLM Compatibility Wrapper

The LLM adapter implementation moved to:

```text
shared/llm/
```

This module remains to preserve existing imports and CLI usage:

```bash
python3 -m modules.llm.llm_adapter "Hello George"
```

New code should prefer `shared.llm`.
