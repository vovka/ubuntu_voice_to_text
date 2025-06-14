"""
State Manager Interface

Abstract base class for managing application state transitions
and providing event hooks for all subsystems.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable

from .voice_typing_state import VoiceTypingState
from .state_transition import StateTransition


class StateManager(ABC):
    """
    Abstract base class for state management.
    
    This interface defines the contract for managing application state
    transitions and providing event hooks for all subsystems.
    """

    @abstractmethod
    def get_current_state(self) -> VoiceTypingState:
        """
        Get the current state of the voice typing system.

        Returns:
            VoiceTypingState: Current state
        """
        pass

    @abstractmethod
    def set_state(self, new_state: VoiceTypingState, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Set a new state for the voice typing system.

        Args:
            new_state: The new state to transition to
            metadata: Optional metadata about the state change

        Returns:
            bool: True if state change was successful, False otherwise
        """
        pass

    @abstractmethod
    def can_transition_to(self, new_state: VoiceTypingState) -> bool:
        """
        Check if transition to the new state is allowed.

        Args:
            new_state: The state to check transition to

        Returns:
            bool: True if transition is allowed, False otherwise
        """
        pass

    @abstractmethod
    def register_state_listener(self, listener: Callable[[StateTransition], None]) -> None:
        """
        Register a listener for state changes.

        Args:
            listener: Function to call when state changes
                     Signature: listener(transition: StateTransition) -> None
        """
        pass

    @abstractmethod
    def unregister_state_listener(self, listener: Callable[[StateTransition], None]) -> None:
        """
        Unregister a state change listener.

        Args:
            listener: The listener function to remove
        """
        pass

    @abstractmethod
    def get_state_history(self, limit: Optional[int] = None) -> list[StateTransition]:
        """
        Get history of state transitions.

        Args:
            limit: Maximum number of transitions to return

        Returns:
            list[StateTransition]: List of recent state transitions
        """
        pass

    @abstractmethod
    def get_state_metadata(self) -> Dict[str, Any]:
        """
        Get metadata associated with the current state.

        Returns:
            Dict[str, Any]: Current state metadata
        """
        pass

    @abstractmethod
    def reset_state(self) -> None:
        """
        Reset the state manager to initial state.
        """
        pass