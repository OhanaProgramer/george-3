#!/usr/bin/env sh

set -eu

cd "$(dirname "$0")/.."

OUTPUT_FILE="${1:-/tmp/george_5sec_mic_check.wav}"

VOICE_INPUT_DEVICE_HINT="${START_TALKING_INPUT_HINT:-reSpeaker}" \
  venv/bin/python3 -m interfaces.voice.mic_capture_test \
    --seconds 5 \
    --output-file "$OUTPUT_FILE"

venv/bin/python3 - "$OUTPUT_FILE" <<'PY'
from pathlib import Path
import sys

from interfaces.voice.continuous_transcription_test import measure_wav_level

path = Path(sys.argv[1])
level = measure_wav_level(path)

print("")
print("George 3 Mic Signal Check")
print("")
print(f"Audio file: {path}")
print(f"RMS: {level['rms_dbfs']} dBFS")
print(f"Peak: {level['max_dbfs']} dBFS")

if level["rms_dbfs"] <= -100 and level["max_dbfs"] <= -100:
    print("Signal: SILENCE / all-zero capture")
else:
    print("Signal: AUDIO PRESENT")
PY
