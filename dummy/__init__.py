"""
Dummy implementations package for the voice-to-text transcriber.

This package contains dummy implementations of all interfaces for testing
and integration verification. Each dummy implementation logs activity
and demonstrates queue interaction without real functionality.
"""

from .dummy_shared_state import DummySharedState
from .dummy_tray_control import DummyTrayControl
from .dummy_keyboard_listener import DummyKeyboardListener
from .dummy_sound_recorder import DummySoundRecorder
from .dummy_noise_cancelling import DummyNoiseCancelling
from .dummy_voice_recognition import DummyVoiceRecognition
from .dummy_output_handler import DummyOutputHandler

__all__ = [
    "DummySharedState",
    "DummyTrayControl",
    "DummyKeyboardListener",
    "DummySoundRecorder",
    "DummyNoiseCancelling",
    "DummyVoiceRecognition",
    "DummyOutputHandler",
]
