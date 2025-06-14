"""
Legacy State Manager Adapter

Adapter to use the existing GlobalState class with the new StateManager interface.
This allows gradual migration to the new interface while maintaining
backward compatibility with existing code.
"""

from typing import Dict, Any, Optional, Callable, Set

from .state_manager import StateManager
from .voice_typing_state import VoiceTypingState
from .state_transition import StateTransition


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