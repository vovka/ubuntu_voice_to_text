"""
Voice Typing package - Modern interface-driven voice typing functionality.
"""

from .config import Config
from .configuration_loader import ConfigurationLoader
from .audio_processor import AudioProcessor
from .tray_icon_manager import TrayIconManager
from .hotkey_manager import HotkeyManager
from .pipeline_voice_typing import PipelineVoiceTyping
from .recognition_sources import (
    VoiceRecognitionSource,
    VoskRecognitionSource,
    WhisperRecognitionSource,
    RecognitionSourceFactory,
)

# Export interfaces for decoupling and modularity
from .interfaces import (
    AudioInputSource,
    OutputActionTarget,
    OutputType,
    OutputDispatcher,
    KeyboardOutputActionTarget,
    StateManager,
    BasicStateManager,
    VoiceTypingState,
    StateTransition,
)

__all__ = [
    "Config",
    "ConfigurationLoader",
    "AudioProcessor",
    "TrayIconManager",
    "HotkeyManager",
    "PipelineVoiceTyping",
    "VoiceRecognitionSource",
    "VoskRecognitionSource",
    "WhisperRecognitionSource",
    "RecognitionSourceFactory",
    # Interfaces
    "AudioInputSource",
    "OutputActionTarget", 
    "OutputType",
    "OutputDispatcher",
    "KeyboardOutputActionTarget",
    "StateManager",
    "BasicStateManager",
    "VoiceTypingState",
    "StateTransition",
]
