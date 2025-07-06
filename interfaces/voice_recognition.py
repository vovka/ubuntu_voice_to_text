"""
Voice recognition interface for the voice-to-text transcriber.

This interface defines the contract for units that convert
audio into recognized text.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .queue_protocol import QueueProtocol


class IVoiceRecognition(ABC):
    """
    Interface for the voice/speech recognition unit.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        audio_input_queue: Optional[QueueProtocol] = None,
        text_output_queue: Optional[QueueProtocol] = None,
    ):
        """Initialize the voice recognition unit with optional configuration and external queues."""
        ...

    @property
    @abstractmethod
    def audio_input_queue(self) -> QueueProtocol:
        """Queue for receiving audio to recognize."""
        ...

    @property
    @abstractmethod
    def text_output_queue(self) -> QueueProtocol:
        """Queue for sending out recognized text."""
        ...

    @abstractmethod
    async def run(self) -> None:
        """
        Main async loop to process audio from input_queue and send recognized text to output_queue.
        """
        ...
