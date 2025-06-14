"""
Audio Input Interface Package

Contains all audio input related interfaces and implementations.
"""

from .audio_input_source import AudioInputSource
from .threaded_audio_input_source import ThreadedAudioInputSource

__all__ = [
    "AudioInputSource",
    "ThreadedAudioInputSource",
]