# Dependency Map

Metadata:
- Purpose: Map current imports and coupling.
- Phase: Architecture review.
- Last updated: 2026-06-01.
- Notes: Planning only; no runtime changes.

## Summary

The current runtime graph is mostly acyclic and layered:

```text
config.settings
    |
    v
leaf capabilities
    |
    v
manual orchestration
    |
    v
voice assistant
```

No circular runtime imports were found in the active modules.

## Current File Imports

### Configuration

`config/settings.py`
-> imports from: standard library only
-> imported by:
- `modules.system.system_status`
- `modules.tailscale.tailscale_status`
- `modules.voice.voice_devices`
- `shared.text_to_speech.voice_speak`
- `modules.voice_capture.voice_capture`
- `shared.speech_to_text.transcription`
- `shared.llm.llm_adapter`
- tests and `prove_george_env.py`

### System

`modules/system/system_status.py`
-> imports from:
- `config.settings`
-> imported by:
- `modules.readiness.readiness_status`
- `tests.test_system_status`

### Tailscale

`modules/tailscale/tailscale_status.py`
-> imports from:
- `config.settings`
-> imported by:
- `modules.readiness.readiness_status`
- `modules.tailscale.tailnet_nodes`
- tests

`modules/tailscale/tailnet_nodes.py`
-> imports from:
- `modules.tailscale.tailscale_status`
-> imported by:
- tests

### Voice

`modules/voice/voice_devices.py`
-> imports from:
- `config.settings`
-> imported by:
- `modules.readiness.readiness_status`
- `modules.voice_capture.voice_capture`
- tests

`shared/text_to_speech/voice_speak.py`
-> imports from:
- `config.settings`
-> imported by:
- `modules.voice_response.voice_response`
- `modules.voice_assistant.voice_assistant`
- `modules.voice.voice_speak` compatibility wrapper
- tests

### Voice Capture

`modules/voice_capture/voice_capture.py`
-> imports from:
- `config.settings`
- `modules.voice.voice_devices`
-> imported by:
- `modules.push_to_talk.push_to_talk`
- `modules.voice_pipeline.voice_pipeline`
- tests

### Transcription

`shared/speech_to_text/transcription.py`
-> imports from:
- `config.settings`
-> imported by:
- `modules.push_to_talk.push_to_talk`
- `modules.voice_pipeline.voice_pipeline`
- `modules.transcription.transcription` compatibility wrapper
- tests

### LLM

`shared/llm/llm_adapter.py`
-> imports from:
- `config.settings`
- runtime lazy import of OpenAI SDK inside `create_openai_client`
-> imported by:
- `modules.voice_assistant.voice_assistant`
- tests

`modules/llm/llm_adapter.py`
-> imports from:
- `shared.llm.llm_adapter`
-> imported by:
- compatibility CLI use

### Orchestration

`modules/push_to_talk/push_to_talk.py`
-> imports from:
- `modules.voice_capture.voice_capture`
- `shared.speech_to_text.transcription`
-> imported by:
- `modules.voice_response.voice_response`
- `modules.voice_assistant.voice_assistant`
- tests

`modules/voice_pipeline/voice_pipeline.py`
-> imports from:
- `modules.voice_capture.voice_capture`
- `shared.speech_to_text.transcription`
-> imported by:
- tests

`modules/voice_response/voice_response.py`
-> imports from:
- `modules.push_to_talk.push_to_talk`
- `shared.text_to_speech.voice_speak`
-> imported by:
- tests

`modules/voice_assistant/voice_assistant.py`
-> imports from:
- `modules.push_to_talk.push_to_talk`
- `shared.llm.llm_adapter`
- `shared.text_to_speech.voice_speak`
-> imported by:
- tests

### Readiness

`modules/readiness/readiness_status.py`
-> imports from:
- `modules.system.system_status`
- `modules.tailscale.tailscale_status`
- `modules.voice.voice_devices`
-> imported by:
- tests

### Placeholder Modules

`modules/actions/__init__.py`
-> imports from: none
-> imported by: none

`modules/conversation/__init__.py`
-> imports from: none
-> imported by: none

`modules/remote_control/__init__.py`
-> imports from: none
-> imported by: none

`modules/speaker_id/__init__.py`
-> imports from: none
-> imported by: none

`modules/wake_listener/__init__.py`
-> imports from: none
-> imported by: none

## Layer Diagram

```text
config.settings
    |
    +--> system_status
    +--> tailscale_status --> tailnet_nodes
    +--> voice_devices --> voice_capture
    +--> voice_speak
    +--> transcription
    +--> llm_adapter

voice_capture + transcription --> voice_pipeline
voice_capture + transcription --> push_to_talk
push_to_talk + voice_speak --> voice_response
push_to_talk + llm_adapter + voice_speak --> voice_assistant

system_status + tailscale_status + voice_devices --> readiness_status
```

## Circular Dependencies

None found in active runtime modules.

## Hidden Coupling

- `data/voice_capture/latest_capture.wav` is a shared artifact path used by
  voice capture and transcription.
- `data/transcription/` is assumed by the transcription module.
- `TRANSCRIPTION_COMMAND` must be valid in the active shell/venv.
- `voice_speak` uses macOS `say`, which speaks through the current system output
  device. `VOICE_OUTPUT_DEVICE_HINT` validates discovery but does not force
  system audio routing.
- `voice_capture` uses `ffmpeg` and AVFoundation device labels.
- `.env` precedence is required because shell variables can conflict with
  project configuration.

## Fragile Paths

- `data/voice_capture/latest_capture.wav`
- `data/transcription/latest_capture.txt`
- `TRANSCRIPTION_COMMAND=whisper` when Codex and terminal PATH differ
- direct absolute package imports such as `modules.voice_capture.voice_capture`

## Duplicated Functionality

No major duplicated runtime functionality was found.

Minor overlap:
- `voice_pipeline`, `push_to_talk`, `voice_response`, and `voice_assistant`
  all orchestrate pieces of the voice flow at different maturity levels.
  This is acceptable today but should collapse into clearer interface-level
  orchestration later.
- Several modules define similar terminal summary helpers. This can later move
  to a shared presentation helper if repetition becomes painful.
