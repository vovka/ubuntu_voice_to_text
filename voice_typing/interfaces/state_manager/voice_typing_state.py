"""
Voice Typing State Enumeration

Defines the possible states of the voice typing system.
"""

from enum import Enum


class VoiceTypingState(Enum):
    """Enumeration of voice typing states."""
    IDLE = "idle"
    LISTENING = "listening"
    FINISH_LISTENING = "finish_listening"
    PROCESSING = "processing"
    ERROR = "error"