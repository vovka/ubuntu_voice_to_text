"""
Voice Typing package - Refactored classes for voice typing functionality.
"""

from .config import Config
from .global_state import GlobalState
from .audio_processor import AudioProcessor
from .tray_icon_manager import TrayIconManager
from .hotkey_manager import HotkeyManager
from .voice_typing_app import VoiceTyping
from .pipeline_voice_typing import PipelineVoiceTyping
from .recognition_sources import (
    VoiceRecognitionSource,
    VoskRecognitionSource,
    WhisperRecognitionSource,
    RecognitionSourceFactory,
)

# Export new interfaces for decoupling and modularity
from .interfaces import (
    AudioInputSource,
    OutputActionTarget,
    OutputType,
    OutputDispatcher,
    KeyboardOutputActionTarget,
    StateManager,
    VoiceTypingState,
    StateTransition,
)

__all__ = [
    "Config",
    "GlobalState",
    "AudioProcessor",
    "TrayIconManager",
    "HotkeyManager",
    "VoiceTyping",
    "PipelineVoiceTyping",
    "VoiceRecognitionSource",
    "VoskRecognitionSource",
    "WhisperRecognitionSource",
    "RecognitionSourceFactory",
    # New interfaces
    "AudioInputSource",
    "OutputActionTarget", 
    "OutputType",
    "OutputDispatcher",
    "KeyboardOutputActionTarget",
    "StateManager",
    "VoiceTypingState",
    "StateTransition",
]
