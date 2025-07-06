"""
Output handler interface for the voice-to-text transcriber.

This interface defines the contract for units that handle
the delivery of recognized text to various outputs.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .queue_protocol import QueueProtocol


class IOutputHandler(ABC):
    """
    Interface for the output handler unit (clipboard, active window, file, etc.).
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        input_queue: Optional[QueueProtocol] = None,
    ):
        """Initialize the output handler unit with optional configuration and external queue."""
        ...

    @property
    @abstractmethod
    def input_queue(self) -> QueueProtocol:
        """Queue for receiving recognized text."""
        ...

    @abstractmethod
    async def run(self) -> None:
        """
        Main async loop to process recognized text and deliver it to the chosen output.
        """
        ...
