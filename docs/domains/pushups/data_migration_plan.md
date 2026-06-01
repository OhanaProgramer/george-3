# Pushups Data Migration Plan

Metadata:
- Purpose: Plan pushup data migration without moving data yet.
- Phase: Pushups domain scaffold v1.
- Last updated: 2026-06-01.
- Notes: No source data has been altered or copied.

## Candidate Authoritative Dataset

Likely authoritative source:

```text
ohanacloud:/srv/george-api/data/pushups/events.ndjson
```

Verification:
- storage format: NDJSON
- event schema: `1`
- event type: `pushups.set`
- entry count: `493`
- date range: `2026-01-01` through `2026-06-01` UTC
- first event timestamp: `2026-01-01T08:00:00.000Z`
- last event timestamp: `2026-06-01T15:20:29.964Z`
- latest cloud data date: `2026-06-01`
- summed reps: `13497`

Related cloud files:

```text
ohanacloud:/srv/george-api/data/pushups/settings.json
ohanacloud:/srv/george-api/data/pushups/derived.json
ohanacloud:/srv/george-api/data/pushups/publish.json
ohanacloud:/srv/george-api/src/domains/pushups/
ohanacloud:/srv/george-api/models/pushupsModel.js
```

Important conflict:
- `settings.json` reports `goal_total: 40000`
- `derived.json` and `publish.json` report `target_total: 30000`

Resolve this before migrating goals or advisor output.

Prior local export:

```text
/Users/jacquewilson/Library/Mobile Documents/iCloud~is~workflow~my~workflows/Documents/George/pushups.json
```

Verification:
- storage format: JSON
- schema version: `2`
- entry count: `165` append-only log entries
- daily record count: `39`
- last entry date: `2026-02-18`
- last log timestamp: `2026-02-18T11:10:21.841Z`
- summary lifetime count: `4365`

This local file appears superseded by the cloud event stream, but should remain
available for comparison during migration.

Do not migrate until authority is confirmed.

## Related Historical Sources

Potential Jan 1-6 historical data:

```text
/Users/jacquewilson/Library/Mobile Documents/com~apple~CloudDocs/Ohana/4. Organize/2026/2026_pushups_backup.txt
```

Verification:
- storage format: CSV text
- entry count: `24`
- date range: `2026-01-01` through `2026-01-06`
- final cumulative count: `476`

Potential superseded shortcut CSV:

```text
/Users/jacquewilson/Library/Mobile Documents/iCloud~is~workflow~my~workflows/Documents/2026_pushups.txt
```

Verification:
- storage format: CSV text
- entry count: `23`
- date range: `2026-01-01` through `2026-01-05`
- final cumulative count: `455`

## Proposed Target Format

Target data should eventually live under:

```text
domains/pushups/data/
```

Suggested future split:

```text
domains/pushups/data/raw/
domains/pushups/data/processed/
```

This scaffold intentionally does not create or populate those subfolders yet.

## Migration Principles

- Copy, do not move, source data.
- Preserve raw source files exactly.
- Normalize into George-owned format in a separate step.
- Make import idempotent.
- Validate counts before and after import.
- Keep append-only event history as the primary source.
- Regenerate daily summaries from events when possible.

## Proposed Verification Before Migration

1. Confirm which source is authoritative.
2. Resolve the goal total conflict between cloud settings and derived output.
3. Confirm whether Jan 1-6 CSV rows are already represented by the cloud
   migrated legacy entries.
4. Confirm whether the tiny shortcut `pushups.json` is scratch/current-state only.
5. Define the target schema in `domains/pushups/models.py`.
6. Add tests for parsing raw cloud NDJSON, local JSON, and CSV without writing data.
7. Run a dry-run import that reports counts only.

## No Data Moved Yet

No data was copied into the repository during this phase.
