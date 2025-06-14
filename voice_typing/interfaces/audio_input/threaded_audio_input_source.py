"""
Threaded Audio Input Source

Base class for audio input sources that run in a separate thread.
This provides common threading functionality for audio input implementations
that need to run continuously in the background.
"""

from abc import abstractmethod
from typing import Callable, Optional
import threading

from .audio_input_source import AudioInputSource


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