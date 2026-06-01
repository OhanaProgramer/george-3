# Risk Assessment

Metadata:
- Purpose: Identify safe and risky reorganization areas.
- Phase: Architecture review.
- Last updated: 2026-06-01.
- Notes: Planning only; no runtime changes.

## Highest Priority Protection

Do not disturb this known-working path during early reorganization:

```text
modules.push_to_talk.push_to_talk
    |
    v
shared.speech_to_text.transcription
    |
    v
shared.llm.llm_adapter
    |
    v
shared.text_to_speech.voice_speak
```

## Files That Should Not Move Yet

These should stay in place until compatibility wrappers and tests are ready:

- `config/settings.py`
- `interfaces/voice/capture/voice_capture.py`
- `shared/speech_to_text/transcription.py`
- `modules/push_to_talk/push_to_talk.py`
- `shared/llm/llm_adapter.py`
- `shared/text_to_speech/voice_speak.py`
- `modules/voice_assistant/voice_assistant.py`

Why:
- They are part of the confirmed working conversational loop.
- They touch hardware, environment, OpenAI, or macOS speech.
- A path/import mistake can break user-facing behavior immediately.

## Files That Should Move Last

- `config/settings.py`
- `modules/voice_assistant/voice_assistant.py`
- `modules/push_to_talk/push_to_talk.py`
- `interfaces/voice/capture/voice_capture.py`
- `shared/speech_to_text/transcription.py`

Why:
- `config/settings.py` is imported broadly and owns `.env` precedence.
- `voice_assistant` is the top-level working orchestration.
- `push_to_talk`, `voice_capture`, and `transcription` are hardware/PATH
  sensitive.

## Files Safe To Move First

Safest candidates:

- `modules/actions/`
- `modules/conversation/`
- `modules/remote_control/`
- `modules/speaker_id/`
- `modules/wake_listener/`

Why:
- placeholder only
- no runtime imports
- no tests depend on behavior

Next safest:

- documentation files
- `prove_george_env.py` to `scripts/`
- empty `shared/`, `scripts/`, `logs/` placeholders

## Medium-Risk Moves

- `modules/system/`
- `modules/tailscale/`
- `modules/readiness/`
- `modules/voice_pipeline/`
- `modules/voice_response/`

Why:
- system/tailscale/readiness are structured and tested but readiness imports
  system, tailscale, and voice discovery.
- voice pipeline and voice response are orchestration modules but not the main
  current assistant path.

## High-Risk Coupling

### Environment Precedence

Risk: shell environment values overriding project `.env`.

Current mitigation:
- `config/settings.py` loads `PROJECT_ROOT/.env` with override behavior.
- `prove_george_env.py` verifies the loaded key matches project `.env`.

Migration concern:
- moving config must preserve this exact behavior.

### Audio Device Labels

Risk: macOS device labels change depending on connected hardware.

Current known setup:
- input: reSpeaker XVF3800 4-Mic Array
- output: MacBook Pro Speakers
- reSpeaker is treated as microphone-only for this setup.

Migration concern:
- do not hard-code device names in future structure.

### Whisper PATH

Risk: Codex and user terminal may see different `PATH` values.

Current mitigation:
- `TRANSCRIPTION_COMMAND` can be `whisper` or an absolute venv path.

Migration concern:
- do not assume Codex can run Whisper-related modules.

### OpenAI SDK/API Key

Risk: SDK availability and API key differ by environment.

Current mitigation:
- LLM tests mock OpenAI.
- project `.env` is authoritative.

Migration concern:
- avoid live API calls in unit tests.

### Runtime Artifact Paths

Risk:
- `data/voice_capture/latest_capture.wav`
- `data/transcription/latest_capture.txt`

Migration concern:
- introduce storage/path helpers before moving data locations.

## Circular Dependency Risk

No circular runtime imports currently exist.

The future risk is introducing domains that import interfaces while interfaces
also import domains. Avoid this by enforcing:

```text
interfaces -> domains -> shared -> core
```

and not the reverse.

## Rollback Strategy

Every migration should be one commit.

Preferred pattern:

1. Add new location.
2. Add compatibility wrapper at old location.
3. Update tests.
4. Run full test suite.
5. Commit.

Rollback:

```bash
git revert <commit>
```

Avoid combining:
- file moves
- behavior changes
- config changes
- dependency upgrades

in one commit.
