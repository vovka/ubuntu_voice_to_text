"""
Interfaces package for the voice-to-text transcriber.

This package contains all the interface definitions for the application's units.
Each interface defines the contract that implementations must follow.
"""

from .queue_protocol import QueueProtocol
from .shared_state import ISharedState
from .tray_control import ITrayControl
from .keyboard_listener import IKeyboardListener
from .sound_recorder import ISoundRecorder
from .noise_cancelling import INoiseCancelling
from .voice_recognition import IVoiceRecognition
from .output_handler import IOutputHandler

__all__ = [
    "QueueProtocol",
    "ISharedState",
    "ITrayControl",
    "IKeyboardListener",
    "ISoundRecorder",
    "INoiseCancelling",
    "IVoiceRecognition",
    "IOutputHandler",
]
