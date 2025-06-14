"""
Basic State Manager Implementation

Basic implementation of StateManager with event handling.
This provides a simple, working implementation that can be used
as a base for more complex state management needs.
"""

from typing import Dict, Any, Optional, Callable, Set

from .state_manager import StateManager
from .voice_typing_state import VoiceTypingState
from .state_transition import StateTransition


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