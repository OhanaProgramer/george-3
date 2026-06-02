# Pushups Timezone Rules

Metadata:
- Purpose: Define timestamp storage and coaching-day calculation rules.
- Phase: Pushup Entry v1.
- Last updated: 2026-06-01.
- Notes: No data migration required.

## Current Event Structure

Pushup events in `domains/pushups/data/events.ndjson` currently store:

- `ts`: UTC ISO timestamp ending in `Z`
- `tz`: timezone context for local coaching-day calculation
- `reps`: positive integer rep count
- `source`: event source such as `web` or `home`
- `schema`, `id`, `type`, `tags`, `note`

Events do not currently persist a `local_date` field. George calculates the
local coaching day from `ts` and `tz`.

## Storage Rules

`ts` is the audit/history timestamp and must stay in UTC ISO format.

Good:

```text
2026-06-02T04:59:00.000Z
```

Not acceptable as the primary timestamp:

```text
2026-06-01 23:59:00 CST
```

George should never overwrite UTC timestamps to make reporting easier.

## Analytics Rules

Analytics group events by the local coaching day calculated from:

```text
ts + tz
```

Example:

```json
{
  "ts": "2026-06-02T04:59:00.000Z",
  "tz": "America/Chicago",
  "reps": 33,
  "source": "web"
}
```

This counts toward:

```text
2026-06-01
```

because `2026-06-02T04:59:00.000Z` is `2026-06-01 11:59 PM` in Central time.

## Affected Metrics

These metrics must use local coaching-day grouping, not raw UTC day grouping:

- today total
- active days
- current streak
- longest streak
- 7-day average
- 14-day average
- 30-day average
- 60-day average
- weekly jump

## Reason

UTC preserves accurate event history across devices and future sync paths.
Local coaching-day grouping preserves user intent for late-night entries.

This matters because pushups done at 11:59 PM Central should count toward the
day Jacque experienced, even though UTC may already be the next calendar day.
