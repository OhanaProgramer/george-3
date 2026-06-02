"""Minimal HTML page rendering helpers."""

from __future__ import annotations

from html import escape


def html_escape(value) -> str:
    """Escape display values for simple HTML pages."""
    return escape("" if value is None else str(value), quote=True)


def render_page(title: str, body: str) -> str:
    """Render a tiny standalone HTML page."""
    safe_title = html_escape(title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    body {{ color: #111827; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem; max-width: 42rem; }}
    label, input, button {{ font-size: 1rem; }}
    input {{ padding: 0.45rem; width: 8rem; }}
    button {{ padding: 0.5rem 0.75rem; }}
    section {{ border-top: 1px solid #e5e7eb; padding: 1rem 0; }}
    .message {{ padding: 0.6rem 0; font-weight: 600; }}
    .error {{ color: #9b1c1c; }}
    .success {{ color: #116329; }}
    dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 0.35rem 1rem; }}
    dt {{ font-weight: 700; }}
    dd {{ margin: 0; }}
    .chart-wrap {{ border: 1px solid #d8dee8; padding: 1rem; }}
    .chart-title {{ color: #667085; margin: 0 0 0.75rem; }}
    .target-note {{ border: 1px solid #fed7c3; color: #7c2d12; margin-top: 1rem; padding: 0.75rem; }}
    .target-note strong {{ display: block; font-size: 1.1rem; margin-bottom: 0.35rem; }}
    svg {{ height: auto; max-width: 100%; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""
