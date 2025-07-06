"""
Shared state interface for the voice-to-text transcriber.

This interface defines the contract for units that manage global state
and propagate state changes throughout the application.
"""

from abc import ABC, abstractmethod
from typing import Optional
from .queue_protocol import QueueProtocol


class ISharedState(ABC):
    """
    Interface for a shared state unit.
    Typically used for propagating and observing global state changes.
    """
    
    def __init__(self, state_queue: Optional[QueueProtocol] = None):
        """Initialize the shared state unit with optional external queue."""
        ...
    
    @property
    @abstractmethod
    def state_queue(self) -> QueueProtocol:
        """A queue for state change events/messages."""
        ...
    
    @abstractmethod
    async def run(self) -> None:
        """
        Main async loop to manage state and process state change events.
        """
        ...