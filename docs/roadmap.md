# Roadmap

Metadata:
- Purpose: Track George 3 build order.
- Phase: LLM Adapter v1.
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
- Voice Pipeline v1
- Push-To-Talk v1
- Voice Response v1
- LLM Adapter v1

## Future

- Input Router
- LLM Voice Response Pipeline
- Wake Listener
- Speaker ID
- Conversation Layer
- Actions Layer
- Remote Control
- Dashboard

## Boundaries

Future modules should be built one at a time. Do not fold wake listening,
speaker identification, LLM calls, conversation logic, actions, remote control,
or dashboard behavior into the current audio modules.
