# Pushups Domain

Metadata:
- Purpose: Define the first George life domain.
- Phase: Pushup Entry v1.
- Last updated: 2026-06-01.
- Notes: Pushup Entry v1 is local-first and append-only.

Pushups is George's first domain for reviewing actions against user-decided
goals.

## Owns

- pushup entries
- pushup daily totals
- pushup goals
- pushup analytics
- pushup recommendations
- pushup migration plans and data contracts

## Does Not Own

- speech
- audio capture
- transcription
- LLM provider access
- voice assistant flows
- web/API infrastructure
- global storage primitives

## Files

- `models.py`: domain object definitions
- `service.py`: read-only access to the active raw event dataset
- `analytics.py`: deterministic snapshot, goal, trend, and risk calculations
- `advisor.py`: rule-based George commentary and recommendations
- `report.py`: plain text Pushups Coach v1 report command
- `data/events.ndjson`: authoritative local raw pushup event dataset
- `data/goal.json`: configurable goal target and coaching window
- `data/backups/`: automatic pre-entry backups before the first local append
- `data/import_staging/`: preserved cloud transfer evidence and source context

## Data Status

`data/events.ndjson` is the authoritative local raw dataset for the Pushups
domain. It was promoted from the staged cloud source:

```text
domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/data/pushups/events.ndjson
```

The `import_staging/` folder is preserved as transfer evidence and should not be
deleted during normal domain work.

Derived analytics are regeneratable from `data/events.ndjson`. Pushup Entry v1
is append-only; it does not edit or rewrite existing events.

## Goal Config

`data/goal.json` owns the current pushup target:

```json
{
  "goal_name": "Birthday Pushups 2026",
  "target_reps": 30000,
  "target_date": "2026-12-22",
  "start_date": "2026-03-28",
  "timezone": "America/Chicago",
  "chart_target": 130
}
```

The goal is configuration, not analytics code. The `start_date` marks the
current coaching window used for the coach-facing active day count.

## Proven Reinforcement Chart

The Pushups page intentionally retains one chart:

- last 60 days as daily bars
- 14-day rolling average as a line
- configured target comparison

This chart has demonstrated long-term behavioral reinforcement value and
supports the mission of discipline and follow-through. It is not considered
dashboard scope expansion.

No additional charts, dashboard cards, heatmaps, monthly views, or yearly views
belong in Pushups without explicit approval.

## Report

Run the current deterministic coach report with:

```bash
python3 -m domains.pushups.report
```

The report is display only. The structured analytics and advisor objects are
the domain product.

## Entry

Pushup Entry v1 appends events through the domain service:

```bash
python3 -m interfaces.web.pushups_app
```

Default URL:

```text
http://127.0.0.1:3033/pushups
```

`BIND_ADDRESS` can be set to a trusted local or future Tailscale address.
Pushups Entry v1 intentionally rejects `0.0.0.0`.
