"""Compatibility namespace for the shared LLM adapter.

Purpose: Preserve old LLM import path during architecture migration.
Phase: Architecture migration.
Last updated: 2026-06-01.
Notes: Import implementation from shared.llm.
"""

from shared.llm.llm_adapter import ask_llm


__all__ = ["ask_llm"]
