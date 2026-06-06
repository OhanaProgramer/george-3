# Anya Audio I/O Path

Metadata:
- Purpose: Track isolated Anya audio input/output tests.
- Phase: Audio foundation v1.
- Last updated: 2026-06-05.
- Notes: No wake word, LLM, assistant runtime, cloud, launchd, or AirPlay automation.

## Goal

Decide within 30 days whether the current external microphone plus Sonos Era 100
SL setup is viable for Anya.

This page documents only the audio foundation path. It does not define full Anya
integration.

## Known Output Paths

### Mini Mac Local Speaker

Working path:

```text
George text -> shared.text_to_speech.voice_speak -> Apple say -> Mini Mac speaker
```

Command:

```bash
python3 -m interfaces.voice.speaker_test
```

Purpose: local Mini Mac speaker output only.

### Sonos Den

Speaker facts:

```text
Name: Den
Model: Sonos Era 100 SL
IP: 192.168.0.99
Control: SoCo / Sonos UPnP over LAN
```

Working path:

```text
George text
-> Apple say creates WAV
-> Mini Mac serves WAV over short-lived local HTTP
-> SoCo play_uri tells Den to fetch WAV
-> Den plays audio
```

Required output format:

```text
WAV
PCM
16-bit
mono
44100 Hz
```

Command:

```bash
python3 -m interfaces.voice.sonos_speaker_test
```

Environment overrides:

```bash
SONOS_SPEAKER_IP=192.168.0.99
SONOS_SPEAKER_NAME=Den
```

## Known Music Path

Apple Music can play to Den when the user manually routes Music.app output to
Den through AirPlay. George can control Music.app orchestration through
AppleScript:

```bash
python3 -m interfaces.tests.music_control_test
```

Current boundary: George does not select or automate AirPlay output.

## Failed Direct AirPlay Routing Path

Den appears in AirPlay discovery:

```bash
dns-sd -B _airplay._tcp local
```

But Den does not appear as a direct Apple `say` target:

```bash
say -a "?" ""
```

Conclusion: `say -a Den` is not a reliable route. For voice output, use the
direct Sonos WAV + SoCo path. For music playback, let Music.app own AirPlay after
manual routing.

## Current Test Commands

Local speaker:

```bash
python3 -m interfaces.voice.speaker_test
```

Sonos speaker:

```bash
python3 -m interfaces.voice.sonos_speaker_test
```

Mic capture:

```bash
VOICE_INPUT_DEVICE_HINT=reSpeaker \
python3 -m interfaces.voice.mic_capture_test
```

Mic capture plus fixed response:

```bash
VOICE_INPUT_DEVICE_HINT=reSpeaker \
python3 -m interfaces.voice.mic_speaker_loop_test --output local
VOICE_INPUT_DEVICE_HINT=reSpeaker \
python3 -m interfaces.voice.mic_speaker_loop_test --output sonos
```

Continuous capture plus whisper.cpp transcription:

```bash
VOICE_INPUT_DEVICE_HINT=reSpeaker \
python3 -m interfaces.voice.continuous_transcription_test
```

Apple Music orchestration:

```bash
python3 -m interfaces.tests.music_control_test
```

## Current Limitations

- No wake word.
- No transcription loop yet.
- No LLM.
- No assistant runtime.
- No AirPlay target selection automation.
- Sonos voice output requires LAN reachability from the Mini Mac to Den.
- Mic capture depends on `VOICE_INPUT_DEVICE_HINT` matching an avfoundation input.
- Mic capture uses `ffmpeg` and duration inspection uses `ffprobe`; on the Mini
  Mac those tools are installed under `/usr/local/bin`, so the isolated mic test
  expands PATH for its own subprocesses.
- Continuous transcription uses `whisper.cpp` through the `whisper-cli`
  subprocess. The first model is stored at
  `shared/models/whisper/ggml-base.en.bin`.
- Do not continue trying to stabilize Python `openai-whisper`, `torch`, `numba`,
  or `llvmlite` inside the George venv for this path.

## Next Steps

1. Confirm `interfaces.voice.sonos_speaker_test` works repeatedly.
2. Confirm `interfaces.voice.mic_capture_test` records usable external mic audio.
3. Confirm `interfaces.voice.mic_speaker_loop_test --output local`.
4. Confirm `interfaces.voice.mic_speaker_loop_test --output sonos`.
5. Only after those pass, add a no-LLM transcription loop:

```bash
python3 -m interfaces.voice.transcription_loop_test
```

Future transcription loop behavior:

```text
capture mic -> transcribe -> speak back "I heard: <transcript>"
```

Future Anya hello-world remains manual until the audio loop is reliable:

```text
User: "Anya, what time is it?"
System: fixed/mock time first, then real time later.
```
