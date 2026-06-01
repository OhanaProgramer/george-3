# Future Architecture

Metadata:
- Purpose: Recommend future George 3 structure.
- Phase: Architecture review.
- Last updated: 2026-06-01.
- Notes: Planning only; no runtime changes.

George's mission is to help Jacque focus efforts by reviewing actions and
assessing whether he is meeting the goals he has decided.

The future architecture should make that mission explicit by separating:

1. Core Platform
2. Shared Modules
3. Domains
4. Interfaces

## Recommended Directory Tree

```text
george-3/
  core/
    config/
    logging/
    storage/
    scheduler/
    events/
    auth/

  shared/
    speech_to_text/
    text_to_speech/
    llm/
    tailscale/
    home_assistant/
    communications/

  domains/
    pushups/
      data/
      models/
      analytics/
      advisor/
      routes/
      tests/
      README.md
      CONTRACT.md
    running/
    finance/

  interfaces/
    voice/
      push_to_talk/
      voice_assistant/
      wake_listener/
    cli/
    web/
    api/

  docs/
  tests/
  data/
  logs/
  scripts/
```

## Current Path to Proposed Path

### Core Platform

`config/settings.py`
-> `core/config/settings.py`

`config/__init__.py`
-> `core/config/__init__.py`

`.env.example`
-> stays at root

`logs/`
-> `core/logging/` may own log setup, but runtime log files can remain in
`logs/`

`data/`
-> keep root `data/` initially; later introduce `core/storage/` helpers before
moving domain-owned data.

### Shared Modules

`modules/transcription/`
-> `shared/speech_to_text/`

`modules/voice/voice_speak.py`
-> `shared/text_to_speech/apple_say.py`

`modules/voice/voice_devices.py`
-> split later:
- audio discovery can live under `shared/audio_devices/`
- Apple voice discovery can live under `shared/text_to_speech/`

`modules/llm/`
-> `shared/llm/`

`modules/tailscale/`
-> `shared/tailscale/`

Future Home Assistant integration:
-> `shared/home_assistant/`

Future communications:
-> `shared/communications/`

### Interfaces

`modules/voice_capture/`
-> `interfaces/voice/capture/`

`modules/push_to_talk/`
-> `interfaces/voice/push_to_talk/`

`modules/voice_pipeline/`
-> likely retire after `interfaces/voice/push_to_talk/` and
`interfaces/voice/assistant/` stabilize, or move to
`interfaces/voice/manual_pipeline/`

`modules/voice_response/`
-> likely retire after `voice_assistant` replaces fixed confirmation, or move to
`interfaces/voice/confirmation_response/`

`modules/voice_assistant/`
-> `interfaces/voice/assistant/`

`modules/wake_listener/`
-> `interfaces/voice/wake_listener/`

Future CLI entry points:
-> `interfaces/cli/`

Future web UI:
-> `interfaces/web/`

Future API:
-> `interfaces/api/`

### Domains

Future pushups:
-> `domains/pushups/`

Future running:
-> `domains/running/`

Future finance:
-> `domains/finance/`

### Existing Placeholder Modules

`modules/speaker_id/`
-> `shared/speaker_id/` or `interfaces/voice/speaker_id/`

Recommendation: start under `shared/speaker_id/` if used by multiple voice
interfaces.

`modules/conversation/`
-> `core/events/` plus `interfaces/voice/session_state/` or
`shared/conversation/`

Recommendation: defer exact placement until conversation memory has a concrete
contract.

`modules/actions/`
-> `core/actions/` or `interfaces/api/actions/`

Recommendation: keep future action execution separate from domains. Domains
should recommend; action layer should execute only authorized actions.

`modules/remote_control/`
-> `core/remote_control/` or `interfaces/api/remote_control/`

Recommendation: defer until authentication and API boundaries exist.

## Important Architecture Boundaries

### Core Platform

Owns:
- configuration
- logging
- storage primitives
- scheduling
- event bus
- authentication

Does not own:
- pushup logic
- voice interaction logic
- LLM prompt semantics

### Shared Modules

Own:
- reusable external integrations
- provider adapters
- speech-to-text
- text-to-speech
- LLM calls
- Tailscale visibility
- communications adapters

Do not own:
- domain goals
- user interface flow
- action authorization policy

### Domains

Own:
- domain data
- domain analytics
- domain recommendations
- domain-specific advisor logic

Do not own:
- voice capture
- LLM provider details
- API server infrastructure
- remote command execution

### Interfaces

Own:
- voice flows
- web flows
- CLI flows
- API request/response surfaces

Do not own:
- provider implementations
- domain analytics
- storage internals

## Pushups Domain Readiness

Pushups can become the first Domain module.

Recommended structure:

```text
domains/pushups/
  README.md
  CONTRACT.md
  data/
    raw/
    processed/
  models/
    workout.py
    set.py
    goal.py
  analytics/
    volume.py
    consistency.py
    progression.py
    recovery.py
  advisor/
    prompt_builder.py
    recommendation.py
    review.py
  routes/
    cli.py
    api.py
  tests/
    test_models.py
    test_analytics.py
    test_advisor.py
```

Data ownership:
- pushup events, sets, sessions, goals, and progress snapshots belong to
  `domains/pushups/`.
- raw import data can live under `domains/pushups/data/raw/`.
- normalized working data can live under `domains/pushups/data/processed/` until
  `core/storage/` exists.

Analytics:
- volume over time
- consistency streaks
- progression toward chosen goals
- recovery and fatigue indicators

Advisor layer:
- interprets analytics in relation to user-decided goals
- produces structured advice
- can later call `shared/llm/` through a narrow adapter

Routes/endpoints:
- `routes/cli.py` for early manual use
- `routes/api.py` later for web/API
- routes should call domain services; they should not compute analytics inline

Why pushups is a good first domain:
- bounded data model
- clear goals
- easy manual verification
- aligns with George's mission of reviewing actions against chosen goals

