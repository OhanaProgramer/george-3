# Migration Plan

Metadata:
- Purpose: Safe sequence for reorganizing George 3.
- Phase: Architecture review.
- Last updated: 2026-06-01.
- Notes: Planning only; no runtime changes.

## Rules

- Preserve the known-working voice assistant path.
- Move one thing at a time.
- Every step must be independently testable.
- Every step must be reversible with a single revert.
- Do not mix behavior changes with file moves.
- Keep compatibility shims where helpful.

Known-working path to protect:

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

## Phase 0: Baseline

1. Run and record baseline tests.

   Test:

   ```bash
   python3 -m unittest discover -s tests
   ```

   Manual smoke test from user terminal/venv:

   ```bash
   python3 -m modules.voice_assistant.voice_assistant
   ```

   Rollback: none needed.

2. Commit architecture docs only.

   Test: docs-only review.

   Rollback: revert docs commit.

## Phase 1: Prepare Namespaces Without Moves

3. Create empty future top-level folders with README-only placeholders:

   ```text
   core/
   domains/
   interfaces/
   ```

   Test:

   ```bash
   python3 -m unittest discover -s tests
   ```

   Rollback: delete placeholder folders.

4. Add import compatibility policy docs.

   Example rule: old imports continue working until the module has moved and
   tests prove both old and new paths.

   Test: docs-only review.

   Rollback: revert docs commit.

## Phase 2: Move Safe Placeholders First

5. Move placeholder modules one at a time.

   Suggested order:

   ```text
   modules/actions -> core/actions or interfaces/api/actions placeholder
   modules/remote_control -> core/remote_control placeholder
   modules/speaker_id -> shared/speaker_id placeholder
   modules/conversation -> shared/conversation placeholder
   modules/wake_listener -> interfaces/voice/wake_listener placeholder
   ```

   Test after each move:

   ```bash
   python3 -m unittest discover -s tests
   ```

   Rollback: revert that one move commit.

## Phase 3: Move Leaf Shared Services

6. Move `modules/llm/` to `shared/llm/`.

   Keep a temporary compatibility wrapper at `modules/llm/llm_adapter.py` that
   imports and re-exports the new implementation.

   Test:

   ```bash
   python3 -m unittest tests.test_llm_adapter
   python3 -m unittest discover -s tests
   python3 -m modules.llm.llm_adapter "Hello George"
   ```

   Rollback: revert the move commit.

7. Move `modules/transcription/` to `shared/speech_to_text/`.

   Keep compatibility wrapper.

   Test:

   ```bash
   python3 -m unittest tests.test_transcription
   python3 -m unittest discover -s tests
   ```

   Manual user-terminal test:

   ```bash
   python3 -m modules.transcription.transcription data/voice_capture/latest_capture.wav
   ```

   Rollback: revert the move commit.

8. Move `modules/voice/voice_speak.py` to `shared/text_to_speech/`.

   Keep compatibility wrapper at current path.

   Test:

   ```bash
   python3 -m unittest tests.test_voice_speak
   python3 -m modules.voice.voice_speak "George speaker test"
   ```

   Rollback: revert the move commit.

9. Split or move `modules/voice/voice_devices.py` last among voice leaf modules.

   Recommendation: do not split until audio discovery and Apple voice discovery
   have separate tests.

   Test:

   ```bash
   python3 -m unittest tests.test_voice_devices
   python3 -m modules.voice.voice_devices
   ```

   Rollback: revert the move commit.

## Phase 4: Move Interfaces

10. Move `modules/voice_capture/` to `interfaces/voice/capture/`.

    Keep compatibility wrapper.

    Test:

    ```bash
    python3 -m unittest tests.test_voice_capture
    python3 -m unittest discover -s tests
    ```

    Manual test:

    ```bash
    python3 -m modules.voice_capture.voice_capture --seconds 3
    ```

    Rollback: revert the move commit.

11. Move `modules/push_to_talk/` to `interfaces/voice/push_to_talk/`.

    Test:

    ```bash
    python3 -m unittest tests.test_push_to_talk
    python3 -m unittest discover -s tests
    ```

    Manual test in user terminal:

    ```bash
    python3 -m modules.push_to_talk.push_to_talk
    ```

    Rollback: revert the move commit.

12. Move `modules/voice_assistant/` to `interfaces/voice/assistant/`.

    This should move late because it is the known-working top-level flow.

    Test:

    ```bash
    python3 -m unittest tests.test_voice_assistant
    python3 -m unittest discover -s tests
    ```

    Manual test:

    ```bash
    python3 -m modules.voice_assistant.voice_assistant
    ```

    Rollback: revert the move commit.

13. Retire or move `voice_pipeline` and `voice_response`.

    Recommendation:
    - keep them until `interfaces/voice/assistant/` is stable
    - then either move as examples or delete in a separate cleanup commit

    Test:

    ```bash
    python3 -m unittest tests.test_voice_pipeline tests.test_voice_response
    ```

    Rollback: revert cleanup commit.

## Phase 5: Move Core Platform

14. Move `config/` to `core/config/`.

    Do this late because nearly every runtime module depends on it.

    Required strategy:
    - create `core/config/settings.py`
    - keep `config/settings.py` as a compatibility wrapper
    - verify `.env` precedence still works

    Test:

    ```bash
    python3 -m unittest tests.test_settings
    python3 prove_george_env.py
    python3 -m unittest discover -s tests
    ```

    Rollback: revert the move commit.

15. Introduce `core/storage/` path helpers.

    Move path construction out of capture/transcription only after tests protect
    behavior.

    Test:

    ```bash
    python3 -m unittest tests.test_voice_capture tests.test_transcription
    ```

    Rollback: revert storage helper commit.

## Phase 6: First Domain

16. Add `domains/pushups/` with no cloud migration yet.

    Include docs, data contracts, and empty tests.

    Test:

    ```bash
    python3 -m unittest discover -s tests
    ```

    Rollback: delete placeholder domain commit.

17. Add pushups model tests.

    Test each domain object without external services.

    Rollback: revert model commit.

18. Add pushups analytics.

    Keep analytics pure and deterministic.

    Rollback: revert analytics commit.

19. Add pushups advisor layer.

    Initially produce structured recommendations without action execution.

    Rollback: revert advisor commit.

20. Add pushups routes/endpoints last.

    Only after domain data and analytics are stable.

    Rollback: revert route commit.

