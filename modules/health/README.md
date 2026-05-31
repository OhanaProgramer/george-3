# Health

Purpose: summarize whether this George node is ready.

This module consumes existing module status objects from system, Tailscale, and
voice. It does not discover hardware or network data directly.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.health.health_status
```

## Product

The structured health object is the product. Terminal output is display only.
