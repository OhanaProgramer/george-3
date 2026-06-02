"""Minimal form parsing helpers."""

from __future__ import annotations

from urllib.parse import parse_qs


def parse_form_data(raw_body: bytes, encoding: str = "utf-8") -> dict[str, str]:
    """Parse application/x-www-form-urlencoded bytes into single-value fields."""
    parsed = parse_qs(raw_body.decode(encoding), keep_blank_values=True)
    return {key: values[0] if values else "" for key, values in parsed.items()}
