# Decisions

Metadata:
- Purpose: Record project decisions and rationale.
- Phase: Foundation.
- Last updated: 2026-05-31.
- Notes: Append decisions as they become stable.

## Active folder name

Decision: use one active working folder for now.

```text
~/Projects/george-3
```

Reason: this keeps development simple while George 3 is still early. Older
folders are archived instead of kept beside the active project.

## Clean-slate George 3

Decision: George 3 starts as a clean root folder.

Reason: George 2 became powerful but too interconnected. George 3 should be
easier to learn, test, and repair.

## Python commands on Mac

Decision: docs should use `python3` in Mac terminal examples.

Reason: macOS commonly provides `python3`, while `python` may not be installed or
may point somewhere unexpected.
