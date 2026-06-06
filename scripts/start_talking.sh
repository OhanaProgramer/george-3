#!/usr/bin/env sh

set -eu

cd "$(dirname "$0")/.."

VOICE_INPUT_DEVICE_HINT="${START_TALKING_INPUT_HINT:-reSpeaker}" \
  venv/bin/python3 -m interfaces.voice.continuous_transcription_test "$@"
