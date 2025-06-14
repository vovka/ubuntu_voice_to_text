"""
Audio Input Source Interface

Abstract base class for audio input sources that capture audio data
for voice recognition processing.
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Optional


class AudioInputSource(ABC):
    """
    Abstract base class for audio input sources.
    
    This interface defines the contract that all audio input implementations
    must follow to provide audio data to the voice typing system.
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the audio input source with configuration.

        Args:
            config: Configuration dictionary containing parameters like:
                - sample_rate: Audio sample rate (e.g., 16000)
                - block_size: Audio block size for processing (e.g., 8000)
                - channels: Number of audio channels (e.g., 1 for mono)
                - dtype: Audio data type (e.g., "int16")

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass

    @abstractmethod
    def start_capture(self, callback: Callable[[bytes], None]) -> bool:
        """
        Start capturing audio data and call the callback with audio chunks.

        Args:
            callback: Function to call with each audio chunk (bytes)
                     Signature: callback(audio_chunk: bytes) -> None

        Returns:
            bool: True if capture started successfully, False otherwise
        """
        pass

    @abstractmethod
    def stop_capture(self) -> None:
        """
        Stop capturing audio data.
        """
        pass

    @abstractmethod
    def is_capturing(self) -> bool:
        """
        Check if audio capture is currently active.

        Returns:
            bool: True if actively capturing audio, False otherwise
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the audio input source is available for use.

        Returns:
            bool: True if available, False otherwise
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up resources used by the audio input source.
        """
        pass

    @abstractmethod
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current audio input device.

        Returns:
            Optional[Dict[str, Any]]: Device information dictionary or None if not available
        """
        pass