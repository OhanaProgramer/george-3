# Architecture

george-3 is organized around small modules.

The root folders are intentionally plain:

- `modules/` contains discrete abilities.
- `shared/` contains code that is truly shared by more than one module.
- `config/` contains non-secret configuration examples.
- `data/` contains local data.
- `logs/` contains runtime logs.
- `tests/` contains project tests.
- `scripts/` contains helper scripts.
- `docs/` contains project notes and decisions.

## Configuration

Configuration lives in `config/settings.py` and reads from environment
variables. It should expose clear constants for modules without secrets or
machine-specific absolute paths.

## Core rule

Do not connect unrelated systems too early.

Build the smallest useful version of one module, test it, write down what it
does, then decide whether another module should depend on it.

## Current Modules

```text
modules/tailscale/
  network and tailnet visibility

modules/voice/
  audio device and Apple voice visibility

modules/system/
  local machine and node visibility

modules/readiness/
  combines readiness information from other modules
```

`modules/readiness/` does not discover hardware or network data directly.
Readiness consumes module contracts.

The readiness module is a reader and summarizer only. It does not fix, restart,
or mutate anything.

Operational readiness belongs in `modules/readiness/`. Human health and fitness
data belongs in a future `modules/body/`. This separation should remain
throughout George 3 development.

## Shared Module Pattern

Each discovery module follows the same small pattern:

1. Discover
2. Normalize
3. Create structured object
4. Display
5. Test
6. Stop

Terminal output is display only. The structured object is the module product.

## Previous generations

Older George folders in `~/Projects/archive` may be read for lessons. They
should not be treated as source code libraries for George 3.

If old code is reused, document:

- what was reviewed
- why reuse was necessary
- what risks come with the reuse
