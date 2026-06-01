# Architecture

Metadata:
- Purpose: Explain George 3 module structure and development pattern.
- Phase: Voice Assistant v1.
- Last updated: 2026-05-31.
- Notes: Architecture guidance only; no implementation steps.

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
config/
  environment-backed local configuration

modules/tailscale/
  network and tailnet visibility

shared/audio_devices/
  device discovery

interfaces/voice/capture/
  short one-shot audio recording

shared/speech_to_text/
  audio file to text

shared/text_to_speech/
  text to Apple speech output

modules/voice_pipeline/
  manual one-shot capture -> transcription

modules/push_to_talk/
  user-triggered start/stop capture -> transcription

modules/voice_response/
  push-to-talk transcript -> fixed spoken confirmation

shared/llm/
  text to configured LLM provider response

modules/voice_assistant/
  push-to-talk transcript -> LLM response -> speech output

modules/system/
  local machine and node visibility

modules/readiness/
  combines readiness information from other modules

modules/wake_listener/
modules/speaker_id/
modules/conversation/
modules/actions/
modules/remote_control/
  future placeholders only
```

Configuration flows in one direction:

```text
.env
  |
  v
config/settings.py
  |
  v
modules/
```

Configuration precedence is intentional:

```text
PROJECT_ROOT/.env
    |
    v
config/settings.py
    |
    v
modules
```

George treats `~/Projects/george-3/.env` as authoritative and overrides
conflicting shell environment values. This keeps behavior consistent across
MacBook, Mini Mac, VSCode, Terminal, and future launchd/systemd services.

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

## Current Audio Pipeline

Manual voice pipeline v1 is intentionally short:

```text
voice_capture
    |
    v
transcription
```

`interfaces/voice/capture/` writes a WAV file. `shared/speech_to_text/` reads an
existing audio file and returns text. `modules/voice_pipeline/` coordinates
those two steps manually in one command.

Current interaction path:

```text
push_to_talk
    |
    v

voice_capture
    |
    v

transcription
```

`modules/push_to_talk/` lets a user manually start recording, manually stop
recording, and then transcribe the captured WAV.

No current module continuously listens, detects wake words, identifies speakers,
manages conversation, calls LLMs, executes actions, performs remote control, or
chooses intelligent responses.

Current response path:

```text
push_to_talk
    |
    v

voice_speak
```

`modules/voice_response/` speaks a fixed confirmation response:

```text
I heard: <transcript>
```

Current conversational path:

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

`modules/voice_assistant/` coordinates the existing modules to hear, think, and
speak once, then exits.

## Future Voice Pipeline

Voice functionality stays split by responsibility:

```text
wake_listener
    |
    v

voice_capture
    |
    v

transcription
    |
    v

speaker_id
    |
    v

conversation
    |
    v

llm
    |
    v

actions / remote_control
    |
    v

voice_speak
```

Near-term roadmap after Voice Assistant v1:

1. Input Router: decide whether transcript should go to the LLM
2. Wake Listener: always-on monitoring, wake phrase detection, automatic trigger
   of the existing pipeline
3. Speaker ID, conversation memory, actions, and remote control as separate
   modules

`interfaces/voice/capture/` is intentionally a small one-shot building block. It
does not continuously monitor audio, detect wake words, transcribe, identify
speakers, call AI, or control remote systems.

`shared/speech_to_text/` consumes an existing audio file and returns text. It
does not capture audio, listen continuously, identify speakers, manage
conversation, or execute actions. The transcription engine is an implementation
detail behind the module contract so Whisper can be replaced later without
changing downstream modules.

Future placeholder modules document expected responsibilities only. They do not
contain runtime implementation.

`shared/llm/` is active as a provider adapter only. It sends provided text to
the configured provider and returns text. It does not decide whether text should
go to the LLM; a future `input_router/` module should own that decision.

## Previous generations

Older George folders in `~/Projects/archive` may be read for lessons. They
should not be treated as source code libraries for George 3.

If old code is reused, document:

- what was reviewed
- why reuse was necessary
- what risks come with the reuse
