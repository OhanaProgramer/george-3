# Pushups Discovery

Metadata:
- Purpose: Inventory current pushup-related assets before migration.
- Phase: Pushups domain scaffold v1.
- Last updated: 2026-06-01.
- Notes: Read-only discovery; no source data was modified or moved.

## Search Scope

Searched:
- `~/Projects/george-3`
- `~/Projects`
- `~/Documents`
- `~/Library/Mobile Documents`
- `~/Applications/Pushups.app`
- `ssh ohanacloud`

Cloud source `ohanacloud` was inspected read-only over SSH. No remote files were
modified or copied.

## Summary

The current George 3 repository contains only pushup planning references. The
authoritative working pushup dataset appears to be the live George API data on
`ohanacloud`:

```text
ohanacloud:/srv/george-api/data/pushups/events.ndjson
```

This is newer and more complete than both the March backup and the local iCloud
exports.

The most complete local iCloud export found is:

```text
/Users/jacquewilson/Library/Mobile Documents/iCloud~is~workflow~my~workflows/Documents/George/pushups.json
```

It appears to be a prior export/snapshot, but final authority should be
confirmed before migration.

## Asset Inventory

| Current Location | Purpose | Authoritative? | Can Regenerate? |
| --- | --- | --- | --- |
| `docs/architecture/future_architecture.md` | Prior architecture plan for `domains/pushups/` ownership and shape. | No | Yes, from architecture decisions. |
| `docs/architecture/migration_plan.md` | Prior staged migration outline for the first domain. | No | Yes, from architecture decisions. |
| `ohanacloud:/srv/george-api/data/pushups/events.ndjson` | Live George API pushup event stream in NDJSON format. | Yes, likely authoritative. | No. This append-only event stream should be preserved exactly. |
| `ohanacloud:/srv/george-api/data/pushups/settings.json` | Live pushup goal/settings file. | Yes for current settings, though goal conflict needs review. | Yes if goals are documented elsewhere; otherwise preserve. |
| `ohanacloud:/srv/george-api/data/pushups/derived.json` | Live derived analytics from event stream/settings. | No, derived from events/settings. | Yes. |
| `ohanacloud:/srv/george-api/data/pushups/publish.json` | Live published summary/advisor payload. | No, derived from events/settings. | Yes. |
| `ohanacloud:/srv/george-api/src/domains/pushups/` | Current cloud pushups service/routes/store/rebuild/settings implementation. | Code source for migration reference. | Yes, from cloud source backup or repo if available. |
| `ohanacloud:/srv/george-api/models/pushupsModel.js` | Current cloud pushups analytics/model code used by rebuild/service code. | Code source for migration reference. | Yes, from cloud source backup or repo if available. |
| `ohanacloud:/srv/george-api/data/pushups/events.ndjson.bak.20260308-151323` | Older live data event-stream backup. | Historical backup. | No, preserve until live source is verified. |
| `ohanacloud:/home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/events.ndjson` | March 25 cloud backup event stream. | Historical backup; superseded by live `/srv` data. | No, preserve until live source is verified. |
| `ohanacloud:/home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/events.ndjson.bak.20260308-151323` | Older cloud event-stream backup. | Historical backup. | No, preserve until newer source is verified. |
| `ohanacloud:/home/george/george-pushups-backup-2026-03-07-0107.tar.gz` | Earlier tarball backup containing pushup data files. | Historical backup. | No, preserve until newer source is verified. |
| `ohanacloud:/home/george/george-pushups-backup-2026-03-07-0106.tar.gz` | Earlier tiny tarball backup. | Probably incomplete/corrupt or placeholder due to 45-byte size. | Unknown. |
| `/Users/jacquewilson/Library/Mobile Documents/iCloud~is~workflow~my~workflows/Documents/George/pushups.json` | Rich PushupTracker JSON dataset with `log`, `daily`, `daily_counts`, `daily_training`, `summary`, and `training_rules`. | Prior local export; likely superseded by cloud. | Partially. Daily and summary can regenerate from log; log cannot be regenerated from rollups. |
| `/Users/jacquewilson/Library/Mobile Documents/com~apple~CloudDocs/Ohana/4. Organize/2026/2026_pushups_backup.txt` | CSV-style backup for early January 2026 pushups. | Possibly historical source for Jan 1-6. | No, unless represented in another source. |
| `/Users/jacquewilson/Library/Mobile Documents/iCloud~is~workflow~my~workflows/Documents/2026_pushups.txt` | CSV-style 2026 pushup log. | Possibly superseded by backup/rich JSON. | No, unless represented in another source. |
| `/Users/jacquewilson/Library/Mobile Documents/com~apple~CloudDocs/Ohana/4. Organize/2026/pushups.json` | Older pushup JSON with `meta`, `schedule`, `counters`, and `history`. | Probably historical or superseded. | Unknown. |
| `/Users/jacquewilson/Library/Mobile Documents/iCloud~is~workflow~my~workflows/Documents/pushups.json` | Tiny JSON entry: timestamp plus pushup count. | No, likely a shortcut scratch/current entry file. | Yes if source event is logged elsewhere. |
| `/Users/jacquewilson/Library/Mobile Documents/iCloud~is~workflow~my~workflows/Documents/2026PushupGoal.json` | Intended goal/config file. Currently empty. | No | Yes, once goal is defined. |
| `/Users/jacquewilson/Library/Mobile Documents/iCloud~dk~simonbs~Scriptable/Documents/PushupBrain.js` | Scriptable writer: validates shortcut input, updates daily totals, lifetime total, and append-only log. | Code source, not data. | Yes, from script backup/version control after migration. |
| `/Users/jacquewilson/Library/Mobile Documents/iCloud~dk~simonbs~Scriptable/Documents/PushupAnalysis.js` | Scriptable read-only weekly analysis over `pushups.json`. | Code source, not data. | Yes, from script backup/version control after migration. |
| `/Users/jacquewilson/Library/Mobile Documents/iCloud~dk~simonbs~Scriptable/Documents/Untitled Script.js` | Export utility for sharing Scriptable `pushups.json`. | Utility, not data. | Yes. |
| `/Users/jacquewilson/Library/Mobile Documents/com~apple~ScriptEditor2/Documents/PushupsBrain.scpt` | AppleScript pushup-related automation. Compiled; contents not inspected as source text. | Code/automation, not data. | Unknown without exported source. |
| `/Users/jacquewilson/Applications/Pushups.app` | macOS Shortcut droplet app for pushups. | Interface/automation, not data. | Yes if Shortcut remains available. |
| `/Users/jacquewilson/Projects/archive/georgesystem-2/george-2/core_logic/health/pushups/` | Older George 2 placeholder pushup module and tests. | No | Yes, but likely not worth migrating directly. |

## Cloud Dataset Observations

Live cloud event stream:
- location: `ohanacloud:/srv/george-api/data/pushups/events.ndjson`
- storage format: NDJSON
- event count: `493`
- first event: `2026-01-01T08:00:00.000Z`, 30 reps
- last event: `2026-06-01T15:20:29.964Z`, 33 reps
- latest cloud data date: `2026-06-01`
- date range: `2026-01-01` through `2026-06-01` UTC
- summed reps: `13497`
- event schema: `1`
- event type: `pushups.set`

Cloud settings:
- location: `ohanacloud:/srv/george-api/data/pushups/settings.json`
- goal total: `40000`
- target date: `2026-12-22`
- target daily override: `0`

Cloud derived analytics:
- location: `ohanacloud:/srv/george-api/data/pushups/derived.json`
- as of: `2026-06-01`
- target total in derived output: `30000`
- current total 2026: `13497`
- average 7d: `113.14`
- average 30d: `95.87`

Note: `settings.json` says goal total `40000`, while `derived.json` and
`publish.json` report target total `30000`. This conflict must be resolved
before migrating goals or advisor output.

## Local Dataset Observations

Rich JSON candidate:
- location: `/Users/jacquewilson/Library/Mobile Documents/iCloud~is~workflow~my~workflows/Documents/George/pushups.json`
- schema version: `2`
- log entries: `165`
- daily records: `39`
- first log entry: `2026-01-10T21:58:25.840Z`, 40 reps
- last log entry: `2026-02-18T11:10:21.841Z`, 25 reps
- last daily date: `2026-02-18`
- lifetime summary: `4365`

Early CSV backup:
- location: `/Users/jacquewilson/Library/Mobile Documents/com~apple~CloudDocs/Ohana/4. Organize/2026/2026_pushups_backup.txt`
- row count: `24`
- first row: `2026-01-01,08:24,20,20,20`
- last row: `2026-01-06,06:35,21,21,476`

Shortcut CSV:
- location: `/Users/jacquewilson/Library/Mobile Documents/iCloud~is~workflow~my~workflows/Documents/2026_pushups.txt`
- row count: `23`
- first row: `2026-01-01,08:24,20,20,20`
- last row: `2026-01-05,18:13,20,120,455`

## Open Questions

- Confirm whether the rich JSON in `Documents/George/pushups.json` is the
  authoritative current dataset or a superseded local export.
- Confirm whether the cloud `events.ndjson` is the authoritative current
  dataset. Current best candidate is live `/srv/george-api/data/pushups/events.ndjson`.
- Resolve cloud goal conflict: `settings.json` goal `40000` vs derived/publish
  target `30000`.
- Confirm whether older local CSV rows are already represented by the cloud
  migrated legacy entries.
- Confirm the goal source for 2026, because `2026PushupGoal.json` is empty.
