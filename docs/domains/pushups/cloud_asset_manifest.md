# Pushups Cloud Asset Manifest

Metadata:
- Purpose: Record cloud pushup assets staged locally for inspection.
- Phase: Pushups domain staging v1.
- Last updated: 2026-06-01.
- Notes: Cloud files were copied read-only from `ohanacloud`; no app behavior changed.

## Staging Location

```text
domains/pushups/data/import_staging/cloud_2026-06-01/
```

The staged files preserve source-path context below the staging folder, such as:

```text
srv/george-api/data/pushups/events.ndjson
home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/events.ndjson
```

## Authoritative Raw Dataset

The authoritative raw dataset appears to be:

```text
ohanacloud:/srv/george-api/data/pushups/events.ndjson
```

Staged copy:

```text
domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/data/pushups/events.ndjson
```

Why:
- It is the live George API event stream.
- It is newer than the `/home/george/george-api-backups/` snapshot.
- It contains the latest observed cloud pushup entry.
- It is append-only NDJSON raw event data, while `derived.json` and
  `publish.json` are generated outputs.

Observed latest staged event:

```text
2026-06-01T15:20:29.964Z, reps=33
```

Because this is a staging snapshot, the live cloud file may advance after this
manifest is written.

## Promotion

Promotion completed:

```text
2026-06-01 10:32:40 MDT
```

Promoted staged source:

```text
domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/data/pushups/events.ndjson
```

Active domain dataset:

```text
domains/pushups/data/events.ndjson
```

Latest event confirmed at promotion:

```text
2026-06-01T15:20:29.964Z, reps=33
```

The staged dataset remains preserved and the active dataset is not wired into
any app runtime path yet.

## Assets

| Source path | Local staged path | Size | Modified date | SHA-256 | Kind | Last pushup entry date |
| --- | --- | ---: | --- | --- | --- | --- |
| `/srv/george-api/data/pushups/events.ndjson` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/data/pushups/events.ndjson` | 89738 | 2026-06-01T09:20:29 | `20bec16f9a968c6f48b2620f51b4f9d88639e07370cf2f77dab1b7b9523832c8` | raw | 2026-06-01 |
| `/srv/george-api/data/pushups/settings.json` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/data/pushups/settings.json` | 102 | 2026-03-25T12:35:49 | `c08fdd9dd1c4fe9cbd8af410159fa7b6d743b3dd741493dcb68d3b8f23842581` | config | target_date=2026-12-22 |
| `/srv/george-api/data/pushups/derived.json` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/data/pushups/derived.json` | 631 | 2026-06-01T09:20:30 | `c9ee629ea49b4d9d0b72416aa9fde4ac60b2a149efb93da44a8fdb97aaa78325` | derived | 2026-06-01 |
| `/srv/george-api/data/pushups/publish.json` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/data/pushups/publish.json` | 9212 | 2026-06-01T09:20:30 | `14999c428891380f678158d1106b3a35e8dec87a226f221fa48131f994cf4f95` | export | 2026-06-01 |
| `/srv/george-api/data/pushups/events.ndjson.bak.20260308-151323` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/data/pushups/events.ndjson.bak.20260308-151323` | 45623 | 2026-03-08T09:13:23 | `7be6dd88c8d9c567b870633717594006a8c860dc60ebdb21c1f465432de0f17a` | backup | not inspected |
| `/srv/george-api/imports/pushups_server.json` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/imports/pushups_server.json` | 31325 | 2026-03-07T08:18:02 | `18f6f63c8d6bc1eaedf1ee4434f239a2e100bd8c05cea61c1bb115038a9afcdb` | export | 2026-02-22 |
| `/srv/george-api/models/pushupsModel.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/models/pushupsModel.js` | 10058 | 2026-03-07T08:18:02 | `2c78fd93f6dd231a70b45498af637b63e8c24ed72d0f94fbad5528498875fadb` | reference code | n/a |
| `/srv/george-api/policy/event_pushups.yaml` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/policy/event_pushups.yaml` | 2866 | 2026-03-07T08:18:02 | `3157b362b4e1cfb3d28491b744a7402cc9c9cd25373da0c636baaa67176e35f9` | config | n/a |
| `/srv/george-api/scripts/clean_pushup_events.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/scripts/clean_pushup_events.js` | 8057 | 2026-03-08T09:13:51 | `bda5ffbf48ef20dfe77998d11a4e4c4a5978bd088f9531ec9823ec1e1d8db81c` | reference code | n/a |
| `/srv/george-api/scripts/export_pushups_ndjson.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/scripts/export_pushups_ndjson.js` | 1558 | 2026-03-07T08:18:02 | `a10ed1636cfd14e8348fc5c65f339404cb67a071c3f466ff0716e236f625b2c0` | reference code | n/a |
| `/srv/george-api/scripts/import_pushups_events.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/scripts/import_pushups_events.js` | 8447 | 2026-03-07T08:18:02 | `d5bbcc9ad014e0a6f55d9258fc9f5912e7feedd2de05e47c57eda3fb94df6993` | reference code | n/a |
| `/srv/george-api/scripts/migrate_pushups_legacy.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/scripts/migrate_pushups_legacy.js` | 1448 | 2026-03-07T08:18:02 | `db2c4ea8d65ca3a1b2f4e48d07c10376cd22adcf9ceb9b752a08350ff406eb15` | reference code | n/a |
| `/srv/george-api/scripts/rebuild_pushups.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/scripts/rebuild_pushups.js` | 427 | 2026-03-07T08:18:02 | `2e9648cec2eab600998d634f9d45fecdb8462cdb2be05a406d348c657dd56742` | reference code | n/a |
| `/srv/george-api/scripts/test_pushups_rebuild.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/scripts/test_pushups_rebuild.js` | 1494 | 2026-03-08T09:13:51 | `fd19853c413ddda835433f1c1694a4436f2ca82666ec7996b4441cc0b8cd41dd` | reference code | n/a |
| `/srv/george-api/src/domains/pushups/index.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/src/domains/pushups/index.js` | 46 | 2026-03-07T08:18:02 | `4d2747cd0bd4bad3f4e8105eaa112f640da8f99991caf7ee38bc887b127dcf68` | reference code | n/a |
| `/srv/george-api/src/domains/pushups/pushups.rebuild.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/src/domains/pushups/pushups.rebuild.js` | 6433 | 2026-03-07T08:18:02 | `0b11257fc1217210d088386cb18408a3271b59d8b718980be8e32d299c5aab56` | reference code | n/a |
| `/srv/george-api/src/domains/pushups/pushups.routes.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/src/domains/pushups/pushups.routes.js` | 5470 | 2026-03-07T08:18:02 | `0731cb3071327ce9dbc56975d053d60f687c520db722b2f0e6a4131087f7ba37` | reference code | n/a |
| `/srv/george-api/src/domains/pushups/pushups.service.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/src/domains/pushups/pushups.service.js` | 2823 | 2026-03-25T12:29:35 | `64b503251617a46239e04eee41654e8f96d6d04c68db9bc3d34556bf487eae74` | reference code | n/a |
| `/srv/george-api/src/domains/pushups/pushups.settings.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/src/domains/pushups/pushups.settings.js` | 2488 | 2026-03-07T08:18:02 | `584f575bdbebea65f813981050c07a386dba25d7c6295a5b88455fd40ae08d1a` | reference code | n/a |
| `/srv/george-api/src/domains/pushups/pushups.store.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/src/domains/pushups/pushups.store.js` | 3551 | 2026-03-07T08:18:02 | `6233536cd19c6e2d228529a5a762a2d13f30dd327b5505f0c6367d1136fa32c7` | reference code | n/a |
| `/srv/george-api/src/domains/pushups/rebuild.js` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/src/domains/pushups/rebuild.js` | 488 | 2026-03-08T09:13:51 | `fdf12cd1d582be5bcfd39d1d1e9114641ec29acd66f1d8a4ddca294fee284d73` | reference code | n/a |
| `/srv/george-api/views/pushups/analytics.ejs` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/views/pushups/analytics.ejs` | 10846 | 2026-03-25T12:29:35 | `9818979f595e219c1cd2e9ceac0b60d67de3b6917b39ba96ee8ddc56dcf0637c` | reference code | n/a |
| `/srv/george-api/views/pushups/log.ejs` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/views/pushups/log.ejs` | 3586 | 2026-03-25T12:29:35 | `945f890069c9104f6160973fe8db9f84a91c155a039e90cfd3c6955138b2960c` | reference code | n/a |
| `/srv/george-api/views/pushups/settings.ejs` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/views/pushups/settings.ejs` | 2662 | 2026-03-07T08:18:02 | `3eaa1371028bc87d910cdb16fd1cd8e38a6255e10e543b497a0c0112f7b7eb42` | reference code | n/a |
| `/srv/george-api/views/pushups/support.ejs` | `domains/pushups/data/import_staging/cloud_2026-06-01/srv/george-api/views/pushups/support.ejs` | 1987 | 2026-03-25T12:29:35 | `c0bbc4fe7e2c7836789462e1e3492e065a605d39cbca769a0ab3d5daf6bc3a23` | reference code | n/a |
| `/home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/events.ndjson` | `domains/pushups/data/import_staging/cloud_2026-06-01/home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/events.ndjson` | 58407 | 2026-03-25T10:52:46 | `3df834ba9b686e5a15f45b44b5e1f76ef1633c9f80f83ea7edaf1241ad6853fb` | raw backup | 2026-03-25 |
| `/home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/settings.json` | `domains/pushups/data/import_staging/cloud_2026-06-01/home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/settings.json` | 102 | 2026-03-22T09:16:28 | `c08fdd9dd1c4fe9cbd8af410159fa7b6d743b3dd741493dcb68d3b8f23842581` | config backup | target_date=2026-12-22 |
| `/home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/derived.json` | `domains/pushups/data/import_staging/cloud_2026-06-01/home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/derived.json` | 627 | 2026-03-25T10:52:47 | `440a9de1b771c70cd48580eb920d09034eabe3d0c4f3548ed550f2f826348b18` | derived backup | 2026-03-25 |
| `/home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/publish.json` | `domains/pushups/data/import_staging/cloud_2026-06-01/home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/publish.json` | 9319 | 2026-03-25T10:52:47 | `51b7a7b8a8d5c87e6bb96d0c90e46f2c0d41a7591a1189d272e5c9ad51dc14b7` | export backup | 2026-03-25 |
| `/home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/events.ndjson.bak.20260308-151323` | `domains/pushups/data/import_staging/cloud_2026-06-01/home/george/george-api-backups/backup-2026-03-25-182934/data/pushups/events.ndjson.bak.20260308-151323` | 45623 | 2026-03-08T09:13:23 | `7be6dd88c8d9c567b870633717594006a8c860dc60ebdb21c1f465432de0f17a` | backup | not inspected |
| `/home/george/george-pushups-backup-2026-03-07-0106.tar.gz` | `domains/pushups/data/import_staging/cloud_2026-06-01/home/george/george-pushups-backup-2026-03-07-0106.tar.gz` | 45 | 2026-03-06T18:06:07 | `85cea451eec057fa7e734548ca3ba6d779ed5836a3f9de14b8394575ef0d7d8e` | backup | n/a |
| `/home/george/george-pushups-backup-2026-03-07-0107.tar.gz` | `domains/pushups/data/import_staging/cloud_2026-06-01/home/george/george-pushups-backup-2026-03-07-0107.tar.gz` | 14716 | 2026-03-06T18:07:46 | `4230b1a516d4103ca2a97107738c169a191fddcc2b5fe82ca2312bebcf49ff39` | backup | n/a |

## Notes

- The staged dataset is not active.
- No cloud files were deleted or overwritten.
- No George 3 runtime code reads from `import_staging/`.
- Derived files and exports are useful for comparison, but should be
  regenerated from the raw event stream during migration.
