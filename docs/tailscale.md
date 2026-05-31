# Tailscale Learning Step

Goal: give George 3 basic visibility into whether this machine is reachable
through Tailscale.

This step is intentionally small.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.tailscale.tailscale_status
```

Show visible Tailnet nodes:

```bash
python3 -m modules.tailscale.tailnet_nodes
```

## Test

```bash
python3 -m unittest tests.test_tailscale tests.test_tailnet_nodes
```

## What it checks

- whether the `tailscale` command is installed
- whether the Tailscale backend says it is running
- this machine's Tailscale IPv4 address
- the configured George node name and role
- visible Tailnet nodes from `tailscale status --json`
- online/offline counts
- node names, operating systems, and Tailscale IPs

## Dashboard direction

The future dashboard should have a node status page.

For now, the module prepares for that by separating:

- data shape: `load_tailnet_status()`
- terminal display: `format_tailnet_summary()`

This keeps the dashboard from depending on terminal text formatting.

## What it does not do

- cloud forwarding
- authentication
- API routing
- remote control
