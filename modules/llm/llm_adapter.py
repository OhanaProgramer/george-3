"""Compatibility wrapper for the shared LLM adapter.

Purpose: Preserve `python3 -m modules.llm.llm_adapter` during migration.
Phase: Architecture migration.
Last updated: 2026-06-01.
Notes: Runtime implementation lives in `shared.llm.llm_adapter`.
"""

from shared.llm.llm_adapter import *  # noqa: F401,F403
from shared.llm.llm_adapter import main


if __name__ == "__main__":
    main()
