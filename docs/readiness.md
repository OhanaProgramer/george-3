# Readiness Aggregator

Metadata:
- Purpose: Document operational readiness aggregation.
- Phase: Readiness v1.
- Last updated: 2026-05-31.
- Notes: Operational readiness only; no audio playback and not human health.

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
- voice devices are ok if configured input and output targets are found
- voice speak config is ok if `VOICE_ENGINE` is supported and `VOICE_NAME` is blank or discovered
- errors mean a core module failed or a required target is missing

## Boundary

The readiness module is a reader and summarizer only.

It does not fix, restart, mutate, route APIs, forward cloud traffic, authenticate,
record audio, transcribe audio, speak aloud, call `speak_text()`, or control
remote machines.

Operational readiness belongs in `modules/readiness/`.

Human health and fitness data belongs in a future `modules/body/`.
