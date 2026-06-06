"""Minimal HTML page rendering helpers."""

from __future__ import annotations

from html import escape


DEFAULT_DEV_HOST = "127.0.0.1"
PUSHUPS_DEV_PORT = 3033
CORE_DEV_PORT = 3034


def html_escape(value) -> str:
    """Escape display values for simple HTML pages."""
    return escape("" if value is None else str(value), quote=True)


def _display_host(host: str | None) -> str:
    if not host or host == "0.0.0.0":
        return DEFAULT_DEV_HOST
    return host


def render_dev_nav(active: str, host: str | None = None) -> str:
    """Render a tiny temporary dev tab bar for local George pages."""
    display_host = _display_host(host)
    items = [
        ("pushups", "Pushups", f"http://{display_host}:{PUSHUPS_DEV_PORT}/pushups"),
        ("core", "Core Dev", f"http://{display_host}:{CORE_DEV_PORT}/dev/core"),
    ]
    links = []
    for key, label, href in items:
        class_name = "active" if key == active else ""
        links.append(
            f'<a class="{class_name}" href="{html_escape(href)}">{html_escape(label)}</a>'
        )

    return f'<nav class="dev-tabs" aria-label="George dev pages">{"".join(links)}</nav>'


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
    .dev-tabs {{ align-items: center; border-bottom: 1px solid #d8dee8; display: flex; gap: 0.35rem; margin: 0 0 1.25rem; padding-bottom: 0.75rem; }}
    .dev-tabs a {{ border: 1px solid transparent; border-radius: 999px; color: #344054; font-weight: 700; padding: 0.4rem 0.75rem; text-decoration: none; }}
    .dev-tabs a:hover {{ background: #f6f8fb; }}
    .dev-tabs a.active {{ background: #eaf7ef; border-color: #b7e2c4; color: #116329; }}
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
