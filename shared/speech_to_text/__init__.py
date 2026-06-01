"""Shared speech-to-text service namespace."""

from .transcription import transcribe_audio

__all__ = ["transcribe_audio"]
