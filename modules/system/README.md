# System

Metadata:
- Purpose: Module overview for local system discovery.
- Phase: System Discovery v1.
- Last updated: 2026-05-31.
- Notes: Read-only machine and node visibility.

Purpose: report what machine George is running on.

This module is read-only. It collects safe local system facts, normalizes them
into a structured object, and prints a short terminal summary.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.system.system_status
```

## Product

The structured object is the product. Terminal output is display only.
