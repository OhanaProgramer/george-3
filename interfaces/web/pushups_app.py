"""Local Pushups Entry v1 web interface."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

from config import settings
from domains.pushups import advisor, analytics, service
from shared.web.forms import parse_form_data
from shared.web.page import html_escape, render_dev_nav, render_page
from shared.web.response import redirect


DEFAULT_PORT = 3033


def _latest_entry_label() -> str:
    latest = service.get_latest_event()
    if not latest:
        return "No entries yet"

    reps = html_escape(latest.get("reps", ""))
    timestamp = html_escape(latest.get("ts", ""))
    return f"{reps} reps at {timestamp}"


def _render_dl(items: list[tuple[str, object]]) -> str:
    rows = "\n".join(
        f"  <dt>{html_escape(label)}</dt><dd>{html_escape(value)}</dd>"
        for label, value in items
    )
    return f"<dl>\n{rows}\n</dl>"


def _svg_points(values: list[float], max_value: float, width: int, height: int) -> str:
    if not values:
        return ""

    count = max(1, len(values) - 1)
    points = []
    for index, value in enumerate(values):
        x = 34 + (index / count) * (width - 54)
        y = height - 26 - ((value / max_value) * (height - 54))
        points.append(f"{x:.1f},{y:.1f}")

    return " ".join(points)


def _render_chart() -> str:
    chart = analytics.get_chart_data()
    daily = chart["daily_totals"]
    rolling = chart["rolling_14d"]
    target = chart["target"]
    current_14d = rolling[-1]["average"] if rolling else 0
    comparison = "above" if current_14d >= target else "below"
    max_value = max(
        [target, 1]
        + [day["total"] for day in daily]
        + [point["average"] for point in rolling]
    )
    width = 720
    height = 320
    chart_bottom = height - 26
    plot_height = height - 54
    bar_gap = 2
    bar_width = max(2, ((width - 54) / max(1, len(daily))) - bar_gap)
    target_y = chart_bottom - ((target / max_value) * plot_height)
    bars = []
    for index, day in enumerate(daily):
        x = 34 + index * ((width - 54) / max(1, len(daily)))
        bar_height = (day["total"] / max_value) * plot_height
        y = chart_bottom - bar_height
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" '
            f'height="{bar_height:.1f}" fill="#8ecdf8"></rect>'
        )

    line_points = _svg_points(
        [point["average"] for point in rolling],
        max_value,
        width,
        height,
    )
    first_label = daily[0]["date"][5:] if daily else ""
    middle_label = daily[len(daily) // 2]["date"][5:] if daily else ""
    last_label = daily[-1]["date"][5:] if daily else ""

    return f"""
<div class="chart-wrap">
  <p class="chart-title">Last 60 days (bars) + 14-day average (line)</p>
  <svg viewBox="0 0 {width} {height}" role="img" aria-label="Last 60 days pushups chart">
    <text x="34" y="22" fill="#667085" font-size="18">{html_escape(int(max_value))}</text>
    <line x1="34" y1="{target_y:.1f}" x2="{width - 20}" y2="{target_y:.1f}" stroke="#f59e7d" stroke-width="2" stroke-dasharray="8 8"></line>
    {''.join(bars)}
    <polyline points="{line_points}" fill="none" stroke="#ff6b2c" stroke-width="4"></polyline>
    <text x="34" y="{height - 4}" fill="#667085" font-size="18">{html_escape(first_label)}</text>
    <text x="{(width / 2) - 34:.1f}" y="{height - 4}" fill="#667085" font-size="18">{html_escape(middle_label)}</text>
    <text x="{width - 74}" y="{height - 4}" fill="#667085" font-size="18">{html_escape(last_label)}</text>
  </svg>
  <div class="target-note">
    <strong>Current 14-day average is {comparison} target.</strong>
    Target: {html_escape(target)} | Current 14d avg: {html_escape(current_14d)}
  </div>
</div>
"""


def render_pushups_page(message: str = "", error: str = "") -> str:
    """Render the simple pushup entry form."""
    goal = service.load_goal()
    coach = analytics.get_analytics()
    assessment = advisor.build_assessment(coach)
    snapshot = coach["snapshot"]
    goal_progress = coach["goal_progress"]
    trend = coach["trend"]
    latest = _latest_entry_label()
    today_total = service.get_today_total()

    message_html = ""
    if message:
        message_html = f'<p class="message success">{html_escape(message)}</p>'
    if error:
        message_html = f'<p class="message error">{html_escape(error)}</p>'

    body = f"""
{render_dev_nav("pushups", settings.BIND_ADDRESS)}
<h1>Pushups Entry</h1>
{message_html}
<section>
  <h2>Add Reps</h2>
  <form action="/pushups" method="post">
    <label for="reps">Reps</label>
    <input id="reps" name="reps" type="number" min="1" step="1" required autofocus>
    <button type="submit">Save</button>
  </form>
</section>
<section>
  <h2>Snapshot</h2>
  {_render_dl([
      ("Today Total", today_total),
      ("Latest Entry", latest),
      ("Total Reps", snapshot["total_reps"]),
      ("Active Days", snapshot["total_active_days"]),
  ])}
</section>
<section>
  <h2>Goal Progress</h2>
  {_render_dl([
      ("Goal", goal.get("goal_name", "")),
      ("Target", f'{goal_progress["target_reps"]} by {goal_progress["target_date"]}'),
      ("Remaining", goal_progress["reps_remaining"]),
      ("Required Per Day", goal_progress["required_per_day"]),
      ("Ahead / Behind", goal_progress["ahead_behind"]),
  ])}
</section>
<section>
  <h2>Trend</h2>
  {_render_dl([
      ("7-Day Average", trend["average_7_day"]),
      ("14-Day Average", trend["average_14_day"]),
      ("30-Day Average", trend["average_30_day"]),
      ("60-Day Average", trend["average_60_day"]),
      ("Lifetime Daily Average", trend["life_time_average"]),
  ])}
  {_render_chart()}
</section>
<section>
  <h2>George Assessment</h2>
  {_render_dl([
      ("Status", assessment["status"]),
      ("Risk", assessment["risk_label"]),
      ("Reason", assessment["reason"]),
      ("Next 7 Days", assessment["next_7_days"]),
  ])}
</section>
"""
    return render_page("Pushups Entry", body)


def save_pushups_form(form: dict[str, str]) -> tuple[bool, str]:
    """Validate and save a pushup entry from submitted form data."""
    try:
        event = service.add_event(form.get("reps", ""), source="web")
    except ValueError as error:
        return False, str(error)

    analytics.write_analytics_json()

    return True, f"Saved {event['reps']} reps."


class PushupsHandler(BaseHTTPRequestHandler):
    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_redirect(self, location: str) -> None:
        status, headers, body = redirect(location)
        self.send_response(status)
        for key, value in headers:
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/pushups":
            self.send_error(404)
            return

        query = parse_qs(parsed.query)
        html = render_pushups_page(
            message=query.get("message", [""])[0],
            error=query.get("error", [""])[0],
        )
        self._send_html(html)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/pushups":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        form = parse_form_data(self.rfile.read(length))
        success, message = save_pushups_form(form)
        key = "message" if success else "error"
        self._send_redirect(f"/pushups?{urlencode({key: message})}")

    def log_message(self, format, *args) -> None:
        return


def run_server(bind_address: str | None = None, port: int = DEFAULT_PORT) -> None:
    """Run the local-only Pushups Entry server."""
    host = bind_address or settings.BIND_ADDRESS
    if host == "0.0.0.0":
        raise ValueError("BIND_ADDRESS=0.0.0.0 is not allowed for Pushups Entry v1")

    server = ThreadingHTTPServer((host, port), PushupsHandler)
    print("George 3 Pushups Entry")
    print(f"URL: http://{host}:{port}/pushups")
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
