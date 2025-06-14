"""
Audio Input Interface

Abstract base class for audio input sources that capture audio data
for voice recognition processing.
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Optional
import threading


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


class ThreadedAudioInputSource(AudioInputSource):
    """
    Base class for audio input sources that run in a separate thread.
    
    This provides common threading functionality for audio input implementations
    that need to run continuously in the background.
    """

    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._capturing = False
        self._callback: Optional[Callable[[bytes], None]] = None

    def start_capture(self, callback: Callable[[bytes], None]) -> bool:
        """Start audio capture in a separate thread."""
        if self._capturing:
            return False
            
        self._callback = callback
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capturing = True
        self._thread.start()
        return True

    def stop_capture(self) -> None:
        """Stop audio capture and wait for thread to finish."""
        if not self._capturing:
            return
            
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._capturing = False
        self._callback = None

    def is_capturing(self) -> bool:
        """Check if currently capturing."""
        return self._capturing

    @abstractmethod
    def _capture_loop(self) -> None:
        """
        Main capture loop that runs in the background thread.
        
        Implementation should:
        1. Check self._stop_event.is_set() periodically
        2. Call self._callback(audio_chunk) with captured audio data
        3. Exit when stop event is set
        """
        pass