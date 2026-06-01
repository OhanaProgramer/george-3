# Transcription

Metadata:
- Purpose: Module overview for audio-to-text transcription.
- Phase: Transcription v1.
- Last updated: 2026-05-31.
- Notes: Reads one audio file and exits; no continuous listening or actions.

Purpose: answer whether George can convert recorded speech into text.

## Approach

Transcription v1 uses the configured local Whisper command-line adapter:

```text
WAV file -> configured transcription command -> transcript text
```

It reads `TRANSCRIPTION_ENGINE`, `TRANSCRIPTION_COMMAND`,
`TRANSCRIPTION_MODEL`, and `TRANSCRIPTION_LANGUAGE` from `config/settings.py`.
The current supported engine is `whisper_cli`. If the configured command is not
available, the module returns a structured error instead of falling back to a
remote service.

`TRANSCRIPTION_COMMAND` can be either a command on the active environment
`PATH`:

```text
TRANSCRIPTION_COMMAND=whisper
```

or an absolute path to a virtual environment executable:

```text
TRANSCRIPTION_COMMAND=/Users/jacquewilson/Projects/george-3/venv/bin/whisper
```

Codex and a user shell may have different `PATH` values. A missing `whisper`
error in one environment does not necessarily mean transcription is broken in
another environment.

This was selected because Whisper is a widely understood baseline for local
speech-to-text, works well with the WAV files produced by `voice_capture/`, and
keeps transcription behind a small module boundary. Downstream modules should
depend on George's structured transcription result, not on Whisper itself.

Alternatives considered:

- Faster-Whisper: likely faster and efficient later, but adds a larger Python
  dependency choice before George needs optimization.
- Apple Speech: native to macOS, but less portable across future George nodes
  and less aligned with the likely Whisper path.
- Other local solutions: possible later, but not needed for the first learning
  version.

The engine should remain replaceable. Future transcription engines should be
able to preserve the same structured result contract.

`modules/transcription/` remains as a compatibility wrapper during the
architecture migration. New code should import from `shared.speech_to_text`.

## Run

From `~/Projects/george-3`:

```bash
python3 -m modules.transcription.transcription
```

```bash
python3 -m modules.transcription.transcription data/voice_capture/latest_capture.wav
```

## Product

The structured result object is the product. Terminal output is display only.

Structured result:

```text
{
  "success": true/false,
  "engine": "whisper_cli",
  "input_file": "...",
  "transcript": "...",
  "duration_seconds": null,
  "message": "...",
  "error": ""
}
```

## Inputs

- an existing WAV file, defaulting to `data/voice_capture/latest_capture.wav`
- transcription settings from `config/settings.py`

## Outputs

- structured transcription result
- transcript text produced by the configured engine

Transcription v1 reads an audio file, produces text, and exits. It does not
listen continuously, monitor microphones, identify speakers, call OpenAI,
execute actions, trigger automation, or manage conversations.

## Future Relationships

Future `speaker_id/`, `conversation/`, and `actions/` modules should depend on
the structured transcription result, not on Whisper-specific implementation
details.
