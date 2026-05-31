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

## Previous generations

Older George folders in `~/Projects/archive` may be read for lessons. They
should not be treated as source code libraries for George 3.

If old code is reused, document:

- what was reviewed
- why reuse was necessary
- what risks come with the reuse
