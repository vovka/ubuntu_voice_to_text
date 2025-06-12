"""
Base class for voice recognition sources.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class VoiceRecognitionSource(ABC):
    """Abstract base class for voice recognition sources."""

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the recognition source with configuration.

        Args:
            config: Configuration dictionary containing necessary parameters

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass

    @abstractmethod
    def process_audio_chunk(self, audio_chunk: bytes) -> None:
        """
        Process a chunk of audio data.

        Args:
            audio_chunk: Raw audio data in bytes
        """
        pass

    @abstractmethod
    def get_result(self) -> Optional[Dict[str, Any]]:
        """
        Get the recognition result.

        Returns:
            Optional[Dict[str, Any]]: Recognition result dictionary or None if no result
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the recognition source is available for use.

        Returns:
            bool: True if available, False otherwise
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up resources used by the recognition source.
        """
        pass
