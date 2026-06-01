"""Compatibility namespace for transcription during architecture migration."""

from shared.speech_to_text.transcription import transcribe_audio

__all__ = ["transcribe_audio"]
