"""
State Manager Interface

Abstract base class for managing application state transitions
and providing event hooks for all subsystems.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Set
from enum import Enum


class VoiceTypingState(Enum):
    """Enumeration of voice typing states."""
    IDLE = "idle"
    LISTENING = "listening"
    FINISH_LISTENING = "finish_listening"
    PROCESSING = "processing"
    ERROR = "error"


class StateTransition:
    """Represents a state transition with optional metadata."""
    
    def __init__(self, from_state: VoiceTypingState, to_state: VoiceTypingState, 
                 metadata: Optional[Dict[str, Any]] = None):
        self.from_state = from_state
        self.to_state = to_state
        self.metadata = metadata or {}
        self.timestamp = self._get_timestamp()
    
    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time
        return time.time()


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


class BasicStateManager(StateManager):
    """
    Basic implementation of StateManager with event handling.
    
    This provides a simple, working implementation that can be used
    as a base for more complex state management needs.
    """

    def __init__(self, initial_state: VoiceTypingState = VoiceTypingState.IDLE):
        """
        Initialize with an initial state.
        
        Args:
            initial_state: The initial state to start with
        """
        self._current_state = initial_state
        self._listeners: Set[Callable[[StateTransition], None]] = set()
        self._history: list[StateTransition] = []
        self._metadata: Dict[str, Any] = {}
        
        # Define valid state transitions
        self._valid_transitions = {
            VoiceTypingState.IDLE: {
                VoiceTypingState.LISTENING,
                VoiceTypingState.ERROR
            },
            VoiceTypingState.LISTENING: {
                VoiceTypingState.FINISH_LISTENING,
                VoiceTypingState.IDLE,
                VoiceTypingState.ERROR
            },
            VoiceTypingState.FINISH_LISTENING: {
                VoiceTypingState.PROCESSING,
                VoiceTypingState.IDLE,
                VoiceTypingState.ERROR
            },
            VoiceTypingState.PROCESSING: {
                VoiceTypingState.IDLE,
                VoiceTypingState.ERROR
            },
            VoiceTypingState.ERROR: {
                VoiceTypingState.IDLE
            }
        }

    def get_current_state(self) -> VoiceTypingState:
        """Get the current state."""
        return self._current_state

    def set_state(self, new_state: VoiceTypingState, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Set a new state with validation and event notification."""
        if not self.can_transition_to(new_state):
            return False
            
        old_state = self._current_state
        self._current_state = new_state
        
        # Update metadata
        if metadata:
            self._metadata.update(metadata)
        
        # Create transition record
        transition = StateTransition(old_state, new_state, metadata)
        self._history.append(transition)
        
        # Notify listeners
        self._notify_listeners(transition)
        
        return True

    def can_transition_to(self, new_state: VoiceTypingState) -> bool:
        """Check if transition is valid."""
        return new_state in self._valid_transitions.get(self._current_state, set())

    def register_state_listener(self, listener: Callable[[StateTransition], None]) -> None:
        """Register a state change listener."""
        self._listeners.add(listener)

    def unregister_state_listener(self, listener: Callable[[StateTransition], None]) -> None:
        """Unregister a state change listener."""
        self._listeners.discard(listener)

    def get_state_history(self, limit: Optional[int] = None) -> list[StateTransition]:
        """Get state transition history."""
        if limit is None:
            return self._history.copy()
        return self._history[-limit:] if limit > 0 else []

    def get_state_metadata(self) -> Dict[str, Any]:
        """Get current state metadata."""
        return self._metadata.copy()

    def reset_state(self) -> None:
        """Reset to initial state."""
        self._current_state = VoiceTypingState.IDLE
        self._history.clear()
        self._metadata.clear()

    def _notify_listeners(self, transition: StateTransition) -> None:
        """Notify all registered listeners of state change."""
        for listener in self._listeners:
            try:
                listener(transition)
            except Exception as e:
                print(f"[StateManager] Error in state listener: {e}")


class LegacyStateManagerAdapter(StateManager):
    """
    Adapter to use the existing GlobalState class with the new StateManager interface.
    
    This allows gradual migration to the new interface while maintaining
    backward compatibility with existing code.
    """

    def __init__(self, global_state):
        """
        Initialize with existing GlobalState instance.
        
        Args:
            global_state: Existing GlobalState instance
        """
        self._global_state = global_state
        self._listeners: Set[Callable[[StateTransition], None]] = set()
        self._history: list[StateTransition] = []
        self._last_state = VoiceTypingState.IDLE

    def get_current_state(self) -> VoiceTypingState:
        """Get current state from GlobalState."""
        state_str = self._global_state.state
        try:
            return VoiceTypingState(state_str)
        except ValueError:
            return VoiceTypingState.IDLE

    def set_state(self, new_state: VoiceTypingState, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Set state in GlobalState and notify listeners."""
        old_state = self.get_current_state()
        self._global_state.state = new_state.value
        
        # Create transition and notify
        transition = StateTransition(old_state, new_state, metadata)
        self._history.append(transition)
        self._notify_listeners(transition)
        
        return True

    def can_transition_to(self, new_state: VoiceTypingState) -> bool:
        """Legacy adapter allows all transitions."""
        return True

    def register_state_listener(self, listener: Callable[[StateTransition], None]) -> None:
        """Register state listener."""
        self._listeners.add(listener)

    def unregister_state_listener(self, listener: Callable[[StateTransition], None]) -> None:
        """Unregister state listener."""
        self._listeners.discard(listener)

    def get_state_history(self, limit: Optional[int] = None) -> list[StateTransition]:
        """Get state history."""
        if limit is None:
            return self._history.copy()
        return self._history[-limit:] if limit > 0 else []

    def get_state_metadata(self) -> Dict[str, Any]:
        """Return empty metadata for legacy adapter."""
        return {}

    def reset_state(self) -> None:
        """Reset to idle state."""
        self._global_state.state = VoiceTypingState.IDLE.value
        self._history.clear()

    def _notify_listeners(self, transition: StateTransition) -> None:
        """Notify listeners of state change."""
        for listener in self._listeners:
            try:
                listener(transition)
            except Exception as e:
                print(f"[LegacyStateManagerAdapter] Error in state listener: {e}")