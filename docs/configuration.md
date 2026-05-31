# Configuration

Metadata:
- Purpose: Document local environment configuration.
- Phase: Foundation configuration.
- Last updated: 2026-05-31.
- Notes: `.env` is local only and must not be committed.

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

VOICE_ENGINE=apple
VOICE_NAME=
VOICE_INPUT_DEVICE_HINT=XVF3800
VOICE_OUTPUT_DEVICE_HINT=system_default
VOICE_PRODUCTION_SPEAKER_HINT=
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

## Voice settings

`VOICE_ENGINE` is currently expected to be `apple`.

`VOICE_NAME` is optional. If it is set, the voice discovery module checks whether
that Apple system voice is available.

`VOICE_INPUT_DEVICE_HINT` should identify the desired microphone. The current
target is:

```text
XVF3800
```

`VOICE_OUTPUT_DEVICE_HINT` is `system_default` for development on the Mac. A
future production speaker can be described with `VOICE_PRODUCTION_SPEAKER_HINT`.

## Not included yet

This configuration step does not add:

- cloud forwarding
- authentication
- API routing
- remote control
