"""
Interface definitions for voice typing system modules.

This package contains abstract base classes that define the contracts
for all major modules in the voice typing system to enable decoupling
and future modularity.
"""

from .audio_input import AudioInputSource
from .output_action import OutputActionTarget, OutputType, OutputDispatcher, KeyboardOutputActionTarget
from .state_manager import StateManager, VoiceTypingState, StateTransition

# Re-export recognition source interface from its existing location
from ..recognition_sources.base import VoiceRecognitionSource

__all__ = [
    "AudioInputSource",
    "OutputActionTarget", 
    "OutputType",
    "OutputDispatcher",
    "KeyboardOutputActionTarget",
    "StateManager",
    "VoiceTypingState",
    "StateTransition",
    "VoiceRecognitionSource",
]