# Pushups Migration Steps

Metadata:
- Purpose: Define safe, reversible steps for making Pushups the first George domain.
- Phase: Pushups domain scaffold v1.
- Last updated: 2026-06-01.
- Notes: Plan only; no pushup data has been migrated.

## Domain Ownership

Owned by `domains/pushups/`:
- pushup entries
- pushup daily totals
- pushup goals
- pushup analytics
- pushup recommendations
- pushup data import contracts

Not owned by `domains/pushups/`:
- speech
- audio capture
- transcription
- LLM provider access
- voice assistant flows
- interface routing
- global storage primitives
- remote control

## Step 1: Domain Scaffold

Create `domains/pushups/` with README and empty module boundaries:
- `models.py`
- `service.py`
- `analytics.py`
- `advisor.py`
- `data/`

Test:

```bash
python3 -m unittest discover -s tests
```

Rollback:
- revert the scaffold commit.

## Step 2: Source Data Contract Tests

Add tests that read copied test fixtures, not live iCloud files.

Expected coverage:
- cloud NDJSON event shape
- cloud settings shape
- cloud derived/publish shape
- rich JSON shape
- CSV backup shape
- date parsing
- count totals
- duplicate handling rules

Rollback:
- revert the tests and fixtures commit.

## Step 3: Dry-Run Import

Create an importer that reads an explicitly provided source path and returns a
structured dry-run result.

Rules:
- no writes
- no source mutation
- report record counts
- report date range
- report suspected duplicate dates
- report goal/settings conflicts

Rollback:
- revert dry-run importer commit.

## Step 4: Normalize Into Domain Data

After dry-run verification, copy raw source data into:

```text
domains/pushups/data/raw/
```

Then generate normalized data into:

```text
domains/pushups/data/processed/
```

Rollback:
- revert copied data and generated processed output commit.

## Step 5: Analytics

Implement pure analytics:
- 14-day total
- 60-day total
- yearly pace
- active days
- consistency

Rollback:
- revert analytics commit.

## Step 6: Advisor

Implement structured George commentary based on analytics and user-defined
goals.

Rollback:
- revert advisor commit.

## Step 7: Interfaces

Add CLI/API routes only after the domain service and analytics are stable.

Rollback:
- revert interface commit.

## Current Stopping Point

The current phase stops after Step 1 planning/scaffold. No data migration has
started.
