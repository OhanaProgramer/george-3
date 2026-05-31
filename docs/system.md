# System Discovery

Goal: report what machine George is running on.

This is read-only discovery only.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.system.system_status
```

## Test

```bash
python3 -m unittest tests.test_system_status
```

## What it checks

- configured node name
- configured node role
- configured environment
- hostname
- operating system
- OS version
- machine architecture
- Python version
- current working directory
- project root
- CPU count
- memory total when practical
- disk total/free when practical
- current timestamp

## Boundary

This module reports system state. It does not change system state.

It does not perform remote control, process management, service restart, file
editing, dashboard UI, or API routing.
