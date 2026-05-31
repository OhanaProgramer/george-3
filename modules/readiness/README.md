# Readiness

Metadata:
- Purpose: Module overview for operational readiness aggregation.
- Phase: Readiness Aggregator v1.
- Last updated: 2026-05-31.
- Notes: Reader/summarizer only; does not mutate system state.

Purpose: summarize whether this George node is ready to operate.

This module consumes existing module status objects from system, Tailscale, and
voice. It does not discover hardware or network data directly.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.readiness.readiness_status
```

## Product

The structured readiness object is the product. Terminal output is display only.
