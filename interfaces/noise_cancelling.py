"""
Noise cancelling interface for the voice-to-text transcriber.

This interface defines the contract for units that preprocess
audio to reduce noise and improve transcription quality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .queue_protocol import QueueProtocol


class INoiseCancelling(ABC):
    """
    Interface for the noise cancelling/preprocessing unit.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, audio_input_queue: Optional[QueueProtocol] = None, audio_output_queue: Optional[QueueProtocol] = None):
        """Initialize the noise cancelling unit with optional configuration and external queues."""
        ...
    
    @property
    @abstractmethod
    def audio_input_queue(self) -> QueueProtocol:
        """Queue for receiving raw audio."""
        ...
    
    @property
    @abstractmethod
    def audio_output_queue(self) -> QueueProtocol:
        """Queue for sending processed audio."""
        ...
    
    @abstractmethod
    async def run(self) -> None:
        """
        Main async loop to process audio from input_queue and send to output_queue.
        """
        ...