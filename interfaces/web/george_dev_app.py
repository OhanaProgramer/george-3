"""Temporary George Core developer web view.

Purpose: Display Core evaluations from domain analytics.json files.
Phase: George Core Dev View v1.
Last updated: 2026-06-03.
Notes: Read-only developer visibility; not a permanent dashboard.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from urllib.parse import urlparse

from config import settings
from core.george_core import dev_view
from shared.web.page import html_escape, render_dev_nav


DEFAULT_PORT = 3034


def _response_class(core_response: object) -> str:
    value = str(core_response or "none").lower()
    if value in {"none", "observe", "report"}:
        return value
    return "unknown"


def _render_signal_list(signals: dict) -> str:
    if not signals:
        return '<li class="muted">none</li>'

    return "\n".join(
        f'<li><span>{html_escape(key)}</span><strong>{html_escape(value)}</strong></li>'
        for key, value in signals.items()
    )


def _render_significant_list(signals: list) -> str:
    if not signals:
        return '<li class="muted">none</li>'

    return "\n".join(f"<li>{html_escape(signal)}</li>" for signal in signals)


def _render_card(evaluation: dict) -> str:
    domain_name = str(evaluation.get("domain", "")).title()
    core_response = str(evaluation.get("core_response", "none"))
    status = evaluation.get("status", "")
    reason = evaluation.get("reason", "")
    last_considered = evaluation.get("last_considered_at", "")
    generated_at = evaluation.get("generated_at", "")
    signals_reviewed = evaluation.get("signals_reviewed") or {}
    significant_signals = evaluation.get("significant_signals") or []
    response_class = _response_class(core_response)

    return f"""
<section class="domain-card">
  <div class="card-top">
    <h2>{html_escape(domain_name)}</h2>
    <span class="response-pill {html_escape(response_class)}">{html_escape(core_response)}</span>
  </div>
  <div class="reason-block">
    <span>Core Response</span>
    <strong>{html_escape(core_response)}</strong>
    <p>{html_escape(reason)}</p>
  </div>
  <dl class="meta-grid">
    <dt>Status</dt><dd>{html_escape(status)}</dd>
    <dt>Last considered</dt><dd>{html_escape(last_considered)}</dd>
    <dt>Analytics generated at</dt><dd>{html_escape(generated_at)}</dd>
  </dl>
  <div class="signal-grid">
    <div>
      <h3>Signals reviewed</h3>
      <ul class="signal-list">
        {_render_signal_list(signals_reviewed)}
      </ul>
    </div>
    <div>
      <h3>Significant signals</h3>
      <ul class="signal-list significant">
        {_render_significant_list(significant_signals)}
      </ul>
    </div>
  </div>
</section>
"""


def render_core_page() -> str:
    """Render the temporary Core dev page."""
    evaluations = dev_view.get_core_evaluations()
    cards = [_render_card(evaluation) for evaluation in evaluations]

    if not cards:
        cards.append('<section class="domain-card"><h2>No Domains</h2><p>No domain analytics files found.</p></section>')

    body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>George Core Dev View</title>
  <style>
    :root {{ color-scheme: light; }}
    * {{ box-sizing: border-box; }}
    body {{
      background: #f6f8fb;
      color: #111827;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.4;
      margin: 0;
      padding: 2rem;
    }}
    main {{ margin: 0 auto; max-width: 68rem; }}
    h1 {{ font-size: 2rem; margin: 0 0 0.35rem; }}
    .subtitle {{ color: #667085; margin: 0 0 1.5rem; }}
    .domain-card {{
      background: #ffffff;
      border: 1px solid #d8dee8;
      border-radius: 8px;
      margin: 0 0 1rem;
      padding: 1.25rem;
    }}
    .card-top {{ align-items: center; display: flex; gap: 1rem; justify-content: space-between; }}
    h2 {{ font-size: 1.35rem; margin: 0; }}
    h3 {{ color: #344054; font-size: 0.95rem; margin: 0 0 0.75rem; }}
    .response-pill {{
      border: 1px solid #cfd7e6;
      border-radius: 999px;
      font-size: 0.9rem;
      font-weight: 700;
      letter-spacing: 0;
      padding: 0.35rem 0.7rem;
      text-transform: uppercase;
    }}
    .response-pill.none {{ background: #eaf7ef; border-color: #b7e2c4; color: #116329; }}
    .response-pill.observe {{ background: #fff6df; border-color: #f2d27c; color: #8a5a00; }}
    .response-pill.report {{ background: #fdecec; border-color: #f3b6b6; color: #9b1c1c; }}
    .response-pill.unknown {{ background: #eef2f7; color: #344054; }}
    .reason-block {{ border-left: 4px solid #8ecdf8; margin: 1rem 0; padding-left: 0.85rem; }}
    .reason-block span {{ color: #667085; display: block; font-size: 0.85rem; }}
    .reason-block strong {{ display: block; font-size: 1.4rem; margin: 0.1rem 0; }}
    .reason-block p {{ margin: 0.25rem 0 0; }}
    .meta-grid {{
      display: grid;
      gap: 0.5rem 1rem;
      grid-template-columns: max-content minmax(0, 1fr);
      margin: 1rem 0;
    }}
    dt {{ color: #667085; font-weight: 700; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    .signal-grid {{ display: grid; gap: 1rem; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .signal-list {{ border-top: 1px solid #edf1f7; list-style: none; margin: 0; padding: 0; }}
    .signal-list li {{
      align-items: center;
      border-bottom: 1px solid #edf1f7;
      display: flex;
      gap: 1rem;
      justify-content: space-between;
      padding: 0.55rem 0;
    }}
    .signal-list span {{ color: #667085; }}
    .signal-list strong {{ text-align: right; }}
    .significant li {{ justify-content: flex-start; }}
    .muted {{ color: #667085; }}
    @media (max-width: 720px) {{
      body {{ padding: 1rem; }}
      .card-top {{ align-items: flex-start; flex-direction: column; }}
      .signal-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    {render_dev_nav("core", settings.BIND_ADDRESS)}
    <h1>George Core Dev View</h1>
    <p class="subtitle">Read-only domain signal observation.</p>
    {''.join(cards)}
  </main>
</body>
</html>
"""
    return body


class GeorgeDevHandler(BaseHTTPRequestHandler):
    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/dev/core":
            self.send_error(404)
            return

        self._send_html(render_core_page())

    def log_message(self, format, *args) -> None:
        return


def run_server(bind_address: str | None = None, port: int = DEFAULT_PORT) -> None:
    """Run the local-only George Core dev server."""
    host = bind_address or settings.BIND_ADDRESS
    if host == "0.0.0.0":
        raise ValueError("BIND_ADDRESS=0.0.0.0 is not allowed for George Core Dev View v1")

    server = ThreadingHTTPServer((host, port), GeorgeDevHandler)
    print("George Core Dev View")
    print(f"URL: http://{host}:{port}/dev/core")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


def main() -> None:
    port = int(os.getenv("PORT", str(DEFAULT_PORT)))
    run_server(port=port)


if __name__ == "__main__":
    main()
