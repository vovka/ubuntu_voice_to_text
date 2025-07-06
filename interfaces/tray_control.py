"""
Tray control interface for the voice-to-text transcriber.

This interface defines the contract for units that manage system tray
functionality and user interaction through the tray icon.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .queue_protocol import QueueProtocol


class ITrayControl(ABC):
    """
    Interface for the tray icon/control unit.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the tray control unit with optional configuration."""
        ...
    
    @property
    @abstractmethod
    def input_queue(self) -> QueueProtocol:
        """Queue for commands or state updates directed to tray."""
        ...
    
    @abstractmethod
    async def run(self) -> None:
        """
        Main async loop to process incoming messages from the input_queue.
        """
        ...