# Readiness

Metadata:
- Purpose: Module overview for operational readiness aggregation.
- Phase: Voice Speak Readiness v1.
- Last updated: 2026-05-31.
- Notes: Reader/summarizer only; does not mutate system state or play audio.

Purpose: summarize whether this George node is ready to operate.

This module consumes existing module status objects from system, Tailscale, and
voice. It does not discover hardware or network data directly. Voice readiness
uses discovery/configuration data only; it does not call `say` or `speak_text()`.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.readiness.readiness_status
```

## Product

The structured readiness object is the product. Terminal output is display only.

Voice summary includes:

```text
Voice: OK
  Devices: OK
  Speak config: OK
```

Voice readiness includes:

- device discovery readiness
- supported speech engine configuration
- `VOICE_NAME` is blank or matches a discovered Apple voice

## Inputs

- system status object
- Tailscale status object
- voice discovery object

## Outputs

- combined readiness object
- one check each for system, Tailscale, and voice
- terminal summary for humans

## Boundaries

Readiness does not repair, restart, mutate, record, transcribe, speak, or call
automation.

## Future Relationships

Future dashboards should consume the readiness object directly.
