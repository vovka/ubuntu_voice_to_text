"""
Voice Recognition Sources package - Abstraction layer for voice recognition engines.
"""

from .base import VoiceRecognitionSource
from .vosk_source import VoskRecognitionSource
from .whisper_source import WhisperRecognitionSource

__all__ = ["VoiceRecognitionSource", "VoskRecognitionSource", "WhisperRecognitionSource"]
