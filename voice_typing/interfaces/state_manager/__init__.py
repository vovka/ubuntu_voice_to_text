"""
State Manager Interface Package

Contains all state management related interfaces and implementations.
"""

from .voice_typing_state import VoiceTypingState
from .state_transition import StateTransition
from .state_manager import StateManager
from .basic_state_manager import BasicStateManager
from .legacy_state_manager_adapter import LegacyStateManagerAdapter

__all__ = [
    "VoiceTypingState",
    "StateTransition",
    "StateManager",
    "BasicStateManager",
    "LegacyStateManagerAdapter",
]