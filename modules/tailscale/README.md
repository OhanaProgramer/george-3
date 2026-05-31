# Tailscale

Metadata:
- Purpose: Module overview for Tailscale visibility.
- Phase: Tailscale Discovery v1.
- Last updated: 2026-05-31.
- Notes: Read-only network visibility; no control actions.

Purpose: help George 3 see whether this machine is reachable through Tailscale.

This is a learning-first module. It answers a few clear questions and does not
try to control the network.

## Questions

- Is Tailscale installed?
- Is Tailscale running?
- What is this machine's Tailscale IP?
- What node is this machine configured to be?
- What other Tailnet nodes are visible?
- Which nodes are online or offline?

## Input

- local `.env` settings through `config/settings.py`
- local `tailscale` command output

## Output

- a small status dictionary
- a readable terminal summary

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.tailscale.tailscale_status
```

To show known Tailnet nodes:

```bash
python3 -m modules.tailscale.tailnet_nodes
```

## Dashboard consideration

`tailnet_nodes.py` returns a simple inventory dictionary with:

- backend state
- tailnet name
- online/offline counts
- one normalized record per node

The terminal summary is only a display layer. A future dashboard should use the
structured inventory data instead of parsing printed text.

## Not included yet

- cloud forwarding
- authentication
- API routing
- remote control

## Boundaries

This module reads local Tailscale command output only. It does not change
Tailnet state, ping nodes, route traffic, or repair connectivity.

## Future Relationships

Readiness consumes the local Tailscale status object. A future dashboard may
display Tailnet inventory from `tailnet_nodes.py`.
