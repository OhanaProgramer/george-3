# george-3

george-3 is the one active working folder for the George 3 learning project.

The goal is to build slowly, one module at a time, with clear boundaries and
simple tests. Previous generations can be used as reference material, but new
George 3 code should be rebuilt in the simplest understandable shape.

## Folder rule

For now, keep only one active working folder:

```text
~/Projects/george-3
```

Older George folders belong in `~/Projects/archive` and are reference only.

## Architecture philosophy

Generation identifies the complete system. Modules identify functionality.

Each major ability should live in a discrete module. A module should be readable
by itself, testable by itself when practical, and safe to replace later.

## Module isolation goals

- Keep modules small.
- Avoid hidden dependencies.
- Prefer obvious file names.
- Write down inputs and outputs.
- Add tests before wiring modules together.
- Use previous generations only as reference unless reuse is clearly justified.

## Configuration

Local machine settings belong in `.env`, which is not committed.

The committed starting point is `.env.example`. See
`docs/configuration.md` for the supported variables and the portable settings
pattern.

## Current Modules

- `modules/tailscale/`: network and tailnet visibility
- `modules/voice/`: audio device and Apple voice visibility
- `modules/system/`: local machine and node visibility
- `modules/health/`: readiness summary from existing module status objects

Each module should discover, normalize, create a structured object, display,
test, and stop. Terminal output is display only. The structured object is the
module product.

## First development focus

The first real module should be communication visibility, starting with
Tailscale status. Do not build cloud forwarding, authentication, or broad routing
until local visibility is stable.
