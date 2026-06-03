"""Temporary George Core developer web view.

Purpose: Display Core evaluations from domain analytics.json files.
Phase: George Core Dev View v1.
Last updated: 2026-06-03.
Notes: Read-only developer visibility; not a permanent dashboard.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from config import settings
from core.george_core import dev_view
from shared.web.page import html_escape, render_page


DEFAULT_PORT = 3034


def _render_signal_list(signals: dict) -> str:
    if not signals:
        return "<li>none</li>"

    return "\n".join(
        f"<li>{html_escape(key)}: {html_escape(value)}</li>"
        for key, value in signals.items()
    )


def _render_significant_list(signals: list) -> str:
    if not signals:
        return "<li>none</li>"

    return "\n".join(f"<li>{html_escape(signal)}</li>" for signal in signals)


def render_core_page() -> str:
    """Render the temporary Core dev page."""
    evaluations = dev_view.get_core_evaluations()

    cards = []
    for evaluation in evaluations:
        domain_name = str(evaluation.get("domain", "")).title()
        core_response = evaluation.get("core_response", "")
        status = evaluation.get("status", "")
        reason = evaluation.get("reason", "")
        last_considered = evaluation.get("last_considered_at", "")
        generated_at = evaluation.get("generated_at", "")
        signals_reviewed = evaluation.get("signals_reviewed") or {}
        significant_signals = evaluation.get("significant_signals") or []
        cards.append(
            f"""
<section>
  <h2>{html_escape(domain_name)}</h2>
  <dl>
    <dt>Core Response</dt><dd>{html_escape(core_response)}</dd>
    <dt>Status</dt><dd>{html_escape(status)}</dd>
    <dt>Reason</dt><dd>{html_escape(reason)}</dd>
    <dt>Last considered</dt><dd>{html_escape(last_considered)}</dd>
    <dt>Generated at</dt><dd>{html_escape(generated_at)}</dd>
  </dl>
  <h3>Signals reviewed</h3>
  <ul>
    {_render_signal_list(signals_reviewed)}
  </ul>
  <h3>Significant signals</h3>
  <ul>
    {_render_significant_list(significant_signals)}
  </ul>
</section>
"""
        )

    if not cards:
        cards.append("<section><h2>No Domains</h2><p>No domain analytics files found.</p></section>")

    body = f"""
<h1>George Core Dev View</h1>
{''.join(cards)}
"""
    return render_page("George Core Dev View", body)


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
    run_server()


if __name__ == "__main__":
    main()
