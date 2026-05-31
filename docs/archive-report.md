# Archive Report

Metadata:
- Purpose: Record folder archive decision.
- Phase: Foundation cleanup.
- Last updated: 2026-05-31.
- Notes: Historical reference only.

## Decision

Use one active George 3 working folder:

```text
~/Projects/george-3
```

Older George folders are archived and should be treated as reference only.

## Active Folder

```text
/Users/jacquewilson/Projects/george-3
```

## Archived Folders

```text
/Users/jacquewilson/Projects/archive/georgesystem-1
/Users/jacquewilson/Projects/archive/georgesystem-2
```

Nothing was deleted.

## Why

The generation naming cleanup created more mental overhead than we need right
now. George 3 is early, so the simplest useful rule is better:

one working folder, older work archived.

## Reference Rule

Archived folders may be inspected for lessons, but George 3 should not copy old
code unless the old implementation is fully understood and reuse is the only
practical solution.

## Configuration Note

The active folder has `.env.example` and ignores real `.env` files.

No real `.env` file was found in the active folder during this cleanup.
