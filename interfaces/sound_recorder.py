"""
Sound recorder interface for the voice-to-text transcriber.

This interface defines the contract for units that capture audio
from the system and manage recording state.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .queue_protocol import QueueProtocol


class ISoundRecorder(ABC):
    """
    Interface for the sound recorder unit.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, audio_output_queue: Optional[QueueProtocol] = None, control_queue: Optional[QueueProtocol] = None):
        """Initialize the sound recorder unit with optional configuration and external queues."""
        ...
    
    @property
    @abstractmethod
    def audio_output_queue(self) -> QueueProtocol:
        """Queue for sending audio chunks or streams."""
        ...
    
    @property
    @abstractmethod
    def control_queue(self) -> QueueProtocol:
        """Queue for receiving control commands (start, stop, etc.)."""
        ...
    
    @abstractmethod
    async def run(self) -> None:
        """
        Main async loop to process control commands and emit audio to audio_output_queue.
        """
        ...