# george-3

Metadata:
- Purpose: Project overview and operating rules.
- Phase: Stabilization after Transcription v1.
- Last updated: 2026-05-31.
- Notes: Keep this file short and beginner-readable.

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

- `config/`: environment-backed local configuration
- `modules/system/`: local machine and node visibility
- `modules/tailscale/`: network and tailnet visibility
- `modules/voice/`: compatibility wrappers for voice CLIs during migration
- `shared/audio_devices/`: audio device and Apple voice discovery
- `interfaces/voice/capture/`: one-shot audio recording
- `shared/speech_to_text/`: existing audio file to text
- `shared/text_to_speech/`: text to Apple speech output
- `modules/voice_pipeline/`: manual one-shot capture -> transcription
- `interfaces/voice/push_to_talk/`: user-triggered start/stop capture -> transcription
- `modules/voice_response/`: fixed spoken confirmation from a push-to-talk transcript
- `shared/llm/`: text to configured LLM provider response
- `interfaces/voice/assistant/`: push-to-talk transcript -> LLM response -> speech output
- `modules/readiness/`: operational readiness summary from existing module status objects

Each module should keep clear inputs, outputs, and boundaries. Terminal output
is display only. The structured object is the module product.

Operational readiness belongs in `modules/readiness/`. Human health and fitness
data belongs in a future `modules/body/`.

## Current audio pipeline

```text
Voice Capture
    |
    v
Transcription
```

## Current response path

```text
Push-To-Talk
    |
    v
Voice Speak
```

Voice Response v1 speaks a fixed confirmation: `I heard: <transcript>`.

## Current conversational path

```text
Push-To-Talk
    |
    v
LLM Adapter
    |
    v
Voice Speak
```

Future placeholder modules exist for wake listening, speaker identification,
conversation, actions, and remote control. They do not implement runtime
behavior yet.

## Current interaction path

```text
Push-To-Talk
    |
    v
Voice Capture
    |
    v
Transcription
```
