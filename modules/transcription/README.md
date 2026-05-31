# Transcription

Metadata:
- Purpose: Module overview for audio-to-text transcription.
- Phase: Transcription v1.
- Last updated: 2026-05-31.
- Notes: Reads one audio file and exits; no continuous listening or actions.

Purpose: answer whether George can convert recorded speech into text.

## Approach

Transcription v1 uses the local Whisper command-line interface as an adapter:

```text
WAV file -> whisper CLI -> transcript text
```

It expects a local `whisper` executable on `PATH`. If Whisper is not installed,
the module returns a structured error instead of falling back to a remote service.

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

Transcription v1 reads an audio file, produces text, and exits. It does not
listen continuously, monitor microphones, identify speakers, call OpenAI,
execute actions, trigger automation, or manage conversations.
