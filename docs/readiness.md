# Readiness Aggregator

Goal: answer whether this George node is ready to operate.

This module combines existing status objects from:

- `modules/system/`
- `modules/tailscale/`
- `modules/voice/`

It does not reimplement discovery logic.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.readiness.readiness_status
```

## Test

```bash
python3 -m unittest tests.test_readiness_status
```

## Rules

- system is ok if core node and host data are present
- system warns if optional resource data is missing
- Tailscale is ok if backend state is `Running` and local Tailscale IP exists
- voice is ok if configured input and output targets are found
- errors mean a core module failed or a required target is missing

## Boundary

The readiness module is a reader and summarizer only.

It does not fix, restart, mutate, route APIs, forward cloud traffic, authenticate,
or control remote machines.

Operational readiness belongs in `modules/readiness/`.

Human health and fitness data belongs in a future `modules/body/`.
