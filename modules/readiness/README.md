# Readiness

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
