"""Compatibility namespace for voice capture during architecture migration."""

from interfaces.voice.capture.voice_capture import capture_audio, start_capture, stop_capture

__all__ = ["capture_audio", "start_capture", "stop_capture"]
