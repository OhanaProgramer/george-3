# System Module Contract

Metadata:
- Purpose: Define system module boundaries.
- Phase: System Discovery v1.
- Last updated: 2026-05-31.
- Notes: Reports system state only; does not change it.

This module answers:

```text
What machine is George running on?
```

## Allowed in v1

- read configured node name, role, environment, and log level
- read hostname
- read operating system and version
- read machine architecture
- read Python version
- read current working directory
- read project root
- read CPU count
- read memory total when practical
- read disk total/free for the project filesystem when practical
- read current timestamp

## Inputs

- local `.env` settings through `config/settings.py`
- read-only local system APIs

## Outputs

- structured system status object
- terminal summary for humans

## Not Allowed in v1

- remote control
- process management
- service restart
- file editing
- shell command execution beyond safe read-only system info
- dashboard UI
- API routing

This module reports system state. It does not change system state.

Future readiness and dashboard surfaces should consume the structured status
object instead of parsing terminal output.
