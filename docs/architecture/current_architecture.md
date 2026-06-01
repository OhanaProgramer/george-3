# Current Architecture Report

Metadata:
- Purpose: Document George 3 as it exists before any reorganization.
- Phase: Architecture review.
- Last updated: 2026-06-01.
- Notes: Planning only; no runtime changes.

George 3 is currently a small, flat Python project organized around independent
modules under `modules/`. The known-working conversational path is:

```text
push_to_talk
    |
    v
transcription
    |
    v
llm_adapter
    |
    v
voice_speak
```

This behavior should remain untouched until migration steps are isolated,
tested, and reversible.

## Major Folders

### `config/`

Purpose: project configuration loader.

Dependencies:
- standard library: `os`, `pathlib`
- reads `PROJECT_ROOT/.env`

Entry points:
- `python3 -m config.settings`

Risk if moved: High.

Why: every runtime module that needs configuration imports `config.settings`.
Moving this early would touch many imports and could break the proven `.env`
precedence behavior.

### `modules/`

Purpose: all current runtime capability modules and placeholder modules.

Dependencies:
- depends heavily on `config/settings.py`
- internal imports are direct absolute imports such as
  `shared.speech_to_text.transcription`

Entry points:
- multiple `python3 -m modules...` CLIs

Risk if moved: High as a whole, Medium to Low per leaf module.

Why: orchestration modules depend on lower-level modules. Leaf modules are safer
to move than orchestration modules, but any move requires import rewrites.

### `modules/system/`

Purpose: read-only local machine and node visibility.

Dependencies:
- `config.settings`
- standard library platform/system APIs

Entry points:
- `python3 -m modules.system.system_status`

Risk if moved: Medium.

Why: used by readiness. It is otherwise isolated and read-only.

### `modules/tailscale/`

Purpose: Tailscale local status and tailnet inventory visibility.

Dependencies:
- `config.settings`
- `tailscale` CLI
- `modules.tailscale.tailscale_status` is used by `tailnet_nodes`

Entry points:
- `python3 -m modules.tailscale.tailscale_status`
- `python3 -m modules.tailscale.tailnet_nodes`

Risk if moved: Medium.

Why: readiness depends on `tailscale_status`; `tailnet_nodes` depends on
`tailscale_status`.

### `shared/audio_devices/` and `modules/voice/`

Purpose: audio device discovery, Apple voice discovery, and old voice CLI
compatibility wrappers.

Dependencies:
- `config.settings`
- macOS `system_profiler`
- macOS `say` through `shared/text_to_speech/`

Entry points:
- `python3 -m modules.voice.voice_devices`
- `python3 -m modules.voice.voice_speak "text"`

Compatibility:
- `modules/voice/voice_devices.py` wraps `shared/audio_devices/voice_devices.py`
- `modules/voice/voice_speak.py` wraps `shared/text_to_speech/voice_speak.py`

Risk if moved again: Medium.

Why: discovery is used by readiness and capture. Speech output lives in
`shared/text_to_speech/`, with the old CLI path retained as a wrapper.

### `interfaces/voice/capture/`

Purpose: one-shot and user-triggered WAV recording.

Dependencies:
- `config.settings`
- `shared.audio_devices.voice_devices`
- `ffmpeg` with macOS AVFoundation

Entry points:
- `python3 -m modules.voice_capture.voice_capture`
- `python3 -m modules.voice_capture.voice_capture --seconds 5`

Risk if moved: High.

Why: it is the microphone boundary and is used by push-to-talk and voice
pipeline. It has hardware coupling and verified working behavior. The old
`modules/voice_capture/` path remains as a compatibility wrapper.

### `shared/speech_to_text/`

Purpose: existing WAV file to transcript text.

Dependencies:
- `config.settings`
- configured Whisper CLI command
- standard library `wave`

Entry points:
- `python3 -m modules.transcription.transcription`
- `python3 -m modules.transcription.transcription data/voice_capture/latest_capture.wav`

Compatibility:
- `modules/transcription/` remains as a wrapper for the old CLI/import path

Risk if moved again: Medium.

Why: used by push-to-talk and voice pipeline. It depends on environment/PATH
configuration that is known to differ between Codex and user terminal.

### `shared/llm/`

Purpose: text to configured LLM provider response.

Dependencies:
- `config.settings`
- OpenAI Python SDK at runtime

Entry points:
- `python3 -m modules.llm.llm_adapter "Hello George"`
- `python3 -m modules.llm.llm_adapter "Explain gravity simply" --tier deep`

Risk if moved: Medium.

Why: it is a leaf service used by voice assistant. It has external provider
configuration and API-key behavior, but tests mock the provider.

Compatibility:
- `modules/llm/` remains as a wrapper around `shared/llm/` during migration.

### `interfaces/voice/push_to_talk/`

Purpose: user-controlled recording and transcription.

Dependencies:
- `interfaces.voice.capture.voice_capture`
- `shared.speech_to_text.transcription`

Entry points:
- `python3 -m modules.push_to_talk.push_to_talk`

Compatibility:
- `modules/push_to_talk/` remains as a wrapper for the old CLI/import path

Risk if moved again: Medium.

Why: it is part of the proven end-to-end voice flow and owns the manual
interaction loop.

### `modules/voice_pipeline/`

Purpose: fixed-duration capture followed by transcription.

Dependencies:
- `interfaces.voice.capture.voice_capture`
- `shared.speech_to_text.transcription`

Entry points:
- `python3 -m modules.voice_pipeline.voice_pipeline`
- `python3 -m modules.voice_pipeline.voice_pipeline --seconds 5`

Risk if moved: Medium.

Why: orchestration only. It can be migrated after its dependencies settle.

### `modules/voice_response/`

Purpose: push-to-talk transcript to fixed spoken confirmation.

Dependencies:
- `interfaces.voice.push_to_talk.push_to_talk`
- `shared.text_to_speech.voice_speak`

Entry points:
- `python3 -m modules.voice_response.voice_response`

Risk if moved: Medium.

Why: orchestration only, but it touches the verified speech output path.

### `modules/voice_assistant/`

Purpose: first hear-think-speak conversational loop.

Dependencies:
- `interfaces.voice.push_to_talk.push_to_talk`
- `shared.llm.llm_adapter`
- `shared.text_to_speech.voice_speak`

Entry points:
- `python3 -m modules.voice_assistant.voice_assistant`

Risk if moved: Very High.

Why: this is the newest known-working end-to-end behavior:
push-to-talk -> transcription -> LLM -> speech output.

### Placeholder Modules

Folders:
- `modules/wake_listener/`
- `modules/speaker_id/`
- `modules/conversation/`
- `modules/actions/`
- `modules/remote_control/`

Purpose: document future responsibilities.

Dependencies:
- none

Entry points:
- none

Risk if moved: Low.

Why: README and namespace-only placeholders. They are safe first candidates for
future namespace experiments.

### `tests/`

Purpose: unit tests for every active module.

Dependencies:
- imports modules directly by current paths
- mocks microphone, Whisper, OpenAI, and speech where needed

Entry points:
- `python3 -m unittest discover -s tests`

Risk if moved: Medium.

Why: tests are the migration safety net. Moving them is possible but should not
happen before runtime package structure stabilizes.

### `docs/`

Purpose: project notes, architecture, status, roadmap, and module-level docs.

Dependencies:
- none at runtime

Entry points:
- none

Risk if moved: Low.

Why: docs are safe to reorganize, but existing links should be updated when
files move.

### `data/`

Purpose: local runtime artifacts.

Current files:
- `data/voice_capture/latest_capture.wav`
- `data/transcription/latest_capture.txt`

Dependencies:
- voice capture writes WAV
- transcription reads WAV and writes transcript files

Entry points:
- none

Risk if moved: High without configuration.

Why: current modules assume `data/voice_capture/latest_capture.wav` and
`data/transcription/` paths. Move only after path settings are configurable.

### `shared/`

Purpose: reserved shared code location.

Dependencies:
- none

Entry points:
- none

Risk if moved: Low.

Why: currently empty.

### `scripts/`

Purpose: reserved helper script location.

Dependencies:
- none

Entry points:
- none

Risk if moved: Low.

Why: currently empty except `.gitkeep`.

### `logs/`

Purpose: reserved runtime logs location.

Dependencies:
- none

Entry points:
- none

Risk if moved: Low.

Why: currently empty except `.gitkeep`.

### Root Files

Important files:
- `.env.example`: committed configuration template
- `.gitignore`: repo hygiene
- `README.md`: project overview
- `prove_george_env.py`: verifies project `.env` precedence

Risk if moved:
- `.env.example`: Medium
- `.gitignore`: High
- `README.md`: Low
- `prove_george_env.py`: Low to Medium

Why: configuration and ignore behavior are foundational. The proof script could
move later into `scripts/` after docs and command examples are updated.
