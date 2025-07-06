"""
Keyboard listener interface for the voice-to-text transcriber.

This interface defines the contract for units that listen for
keyboard hotkeys and publish keyboard events.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .queue_protocol import QueueProtocol


class IKeyboardListener(ABC):
    """
    Interface for the keyboard hotkey listener unit.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the keyboard listener unit with optional configuration."""
        ...
    
    @property
    @abstractmethod
    def output_queue(self) -> QueueProtocol:
        """Queue for publishing detected hotkey events."""
        ...
    
    @abstractmethod
    async def run(self) -> None:
        """
        Main async loop to listen for keyboard input and post events to output_queue.
        """
        ...