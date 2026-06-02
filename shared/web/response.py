"""Minimal HTTP response helpers."""

from __future__ import annotations


def redirect(location: str) -> tuple[int, list[tuple[str, str]], bytes]:
    """Return a simple 303 redirect response tuple."""
    return 303, [("Location", location)], b""
