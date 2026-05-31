# Configuration

George 3 uses environment variables for machine-specific settings.

The real local file is:

```text
.env
```

Do not commit `.env`. Each machine gets its own `.env`.

The committed example file is:

```text
.env.example
```

Use `.env.example` as a starting point when setting up a new machine.

## Supported variables

```text
GEORGE_NODE_NAME=macpro-dev
GEORGE_NODE_ROLE=dev
GEORGE_ENV=development
GEORGE_LOG_LEVEL=info

TAILSCALE_EXPECTED=true
TAILSCALE_TIMEOUT_SECONDS=5
```

## Node name

`GEORGE_NODE_NAME` identifies the device.

Examples:

- `macpro-dev`
- `minimac-home`
- `cloud-gateway`

## Node role

`GEORGE_NODE_ROLE` identifies what the device is allowed to do.

Examples:

- `dev`
- `home-server`
- `cloud-gateway`
- `worker`

The role should guide future behavior. For example, a `dev` node can run local
experiments, while a future `cloud-gateway` node may be allowed to handle
network-facing work.

## Portable paths

George 3 should move cleanly between a Mac Pro now and a Mini later.

Avoid hard-coded absolute paths. When a path is needed, generate it from the
project root in `config/settings.py`.

## Python settings module

Modules should import clear constants from:

```text
config/settings.py
```

Example:

```python
from config.settings import GEORGE_NODE_NAME, GEORGE_NODE_ROLE
```

On Mac, run the settings check with:

```bash
python3 -m config.settings
```

`config/settings.py` loads simple `KEY=VALUE` lines from `.env` automatically.
It should never print secrets. Modules should only expose values they actually
need.

## Not included yet

This configuration step does not add:

- cloud forwarding
- authentication
- API routing
- remote control
