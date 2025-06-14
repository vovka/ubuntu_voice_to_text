"""
State Transition Data Class

Represents a state transition with optional metadata.
"""

from typing import Dict, Any, Optional

from .voice_typing_state import VoiceTypingState


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