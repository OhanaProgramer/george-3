# Pushups Domain

Metadata:
- Purpose: Define the first George life domain.
- Phase: Pushups Coach v1.
- Last updated: 2026-06-01.
- Notes: Active raw dataset is read-only; no write path or app wiring yet.

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
- `data/import_staging/`: preserved cloud transfer evidence and source context

## Data Status

`data/events.ndjson` is the authoritative local raw dataset for the Pushups
domain. It was promoted from the staged cloud source:

```text
domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/data/pushups/events.ndjson
```

The `import_staging/` folder is preserved as transfer evidence and should not be
deleted during normal domain work.

Derived analytics are regeneratable from `data/events.ndjson`. Editing and
writing are not active yet; this domain currently reads pushup events only.

## Goal Config

`data/goal.json` owns the current pushup target:

```json
{
  "goal_name": "Birthday Pushups 2026",
  "target_reps": 30000,
  "target_date": "2026-12-22",
  "start_date": "2026-03-28"
}
```

The goal is configuration, not analytics code. The `start_date` marks the
current coaching window used for the coach-facing active day count.

## Report

Run the current deterministic coach report with:

```bash
python3 -m domains.pushups.report
```

The report is display only. The structured analytics and advisor objects are
the domain product.
