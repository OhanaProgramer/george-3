# Roadmap

## Phase 0: Foundation

- Create the generation root.
- Add starter docs.
- Keep the structure simple.
- Do not copy old generation code.

## Phase 1: Communication visibility

- Build a small Tailscale status module.
- Answer whether Tailscale is installed.
- Answer whether Tailscale is running.
- Print this machine's Tailscale IP when available.
- Show visible Tailnet nodes in a dashboard-ready data shape.
- Keep this as visibility only.

## Phase 2: Local API shell

- Add a small local API readiness endpoint.
- Keep it separate from cloud forwarding.

## Phase 3: External data modules

- Add weather.
- Add AI API.
- Add Schwab only after the simpler communication path is stable.

## Phase 4: Device and life modules

- Add read-only voice/audio discovery.
- Add speaker playback later as a separate module.
- Add microphone capture later as a separate module.
- Add human body modules later under `modules/body/`.
