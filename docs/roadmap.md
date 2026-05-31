# Roadmap

Metadata:
- Purpose: Track George 3 build order.
- Phase: Stabilization after Transcription v1.
- Last updated: 2026-05-31.
- Notes: Keep future work separated from current implementation.

## Phase 0: Foundation

- Create the generation root.
- Add starter docs.
- Keep the structure simple.
- Do not copy old generation code.

## Completed

- System Discovery v1
- Tailscale Discovery v1
- Voice Discovery v1
- Voice Speak v1
- Readiness v1
- Voice Capture v1
- Transcription v1

## Future

- Speaker ID
- Wake Listener
- Conversation Layer
- Actions Layer
- Dashboard

## Boundaries

Future modules should be built one at a time. Do not fold wake listening,
speaker identification, conversation logic, actions, or dashboard behavior into
the current audio modules.
