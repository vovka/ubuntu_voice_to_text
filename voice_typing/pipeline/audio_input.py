"""
SoundDevice-based audio input implementation for the pipeline.

Provides a concrete implementation of AudioInputSource using sounddevice.
"""

import queue
import threading
from typing import Dict, Any, Optional, Callable
from ..interfaces import AudioInputSource


class SoundDeviceAudioInput(AudioInputSource):
    """
    Audio input implementation using the sounddevice library.

    This provides real audio capture functionality for the voice typing system.
    Uses a queue-based approach to prevent audio callback blocking.
    """

    def __init__(self):
        self._stream = None
        self._callback: Optional[Callable[[bytes], None]] = None
        self._config: Optional[Dict[str, Any]] = None
        self.sd = None

        # Queue-based audio processing to prevent callback blocking
        self._audio_queue: Optional[queue.Queue] = None
        self._processing_thread: Optional[threading.Thread] = None
        self._stop_processing = threading.Event()

        # Queue parameters
        self._max_queue_size = 100  # Maximum number of audio chunks in queue

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize sounddevice with the given configuration."""
        try:
            import sounddevice as sd
            self.sd = sd
            self._config = config

            # Use smaller default block size for better real-time performance
            if 'block_size' not in self._config:
                self._config['block_size'] = 4000  # Smaller default for reduced latency

            return True
        except ImportError:
            print("[SoundDeviceAudioInput] sounddevice not available")
            return False

    def start_capture(self, callback: Callable[[bytes], None]) -> bool:
        """Start audio capture with the provided callback."""
        if self._stream is not None:
            print("[SoundDeviceAudioInput] Already capturing")
            return False

        if not self.sd:
            print("[SoundDeviceAudioInput] Not initialized")
            return False

        self._callback = callback

        # Initialize queue and processing thread
        self._audio_queue = queue.Queue(maxsize=self._max_queue_size)
        self._stop_processing.clear()

        # Start processing thread before audio stream
        self._processing_thread = threading.Thread(
            target=self._audio_processing_loop,
            daemon=True
        )
        self._processing_thread.start()

        def audio_callback(indata, frames, time, status):
            """Internal callback that enqueues data without blocking."""
            if status:
                print(f"[SoundDeviceAudioInput] Audio callback status: {status}")

            # Convert numpy array to bytes
            audio_bytes = indata.tobytes()

            # Enqueue audio data without blocking
            try:
                self._audio_queue.put_nowait(audio_bytes)
            except queue.Full:
                # Drop oldest data if queue is full to prevent memory issues
                try:
                    self._audio_queue.get_nowait()  # Remove oldest
                    self._audio_queue.put_nowait(audio_bytes)  # Add newest
                    print("[SoundDeviceAudioInput] Audio queue full, dropped oldest chunk")
                except queue.Empty:
                    pass  # Queue was cleared by another thread

        try:
            self._stream = self.sd.RawInputStream(
                samplerate=self._config['sample_rate'],
                blocksize=self._config.get('block_size', 4000),
                dtype=self._config.get('dtype', 'int16'),
                channels=self._config.get('channels', 1),
                callback=audio_callback
            )
            self._stream.start()
            print("[SoundDeviceAudioInput] Started audio capture with non-blocking processing")
            return True

        except Exception as e:
            print(f"[SoundDeviceAudioInput] Failed to start capture: {e}")
            self._cleanup_resources()
            return False

    def _audio_processing_loop(self) -> None:
        """
        Background thread that processes audio data from the queue.
        This prevents blocking of the audio callback.
        """
        print("[SoundDeviceAudioInput] Audio processing thread started")

        while not self._stop_processing.is_set():
            try:
                # Get audio data from queue with timeout
                audio_bytes = self._audio_queue.get(timeout=0.1)

                # Process audio data through callback if available
                if self._callback:
                    self._callback(audio_bytes)

            except queue.Empty:
                # Timeout occurred, check if we should continue
                continue
            except Exception as e:
                print(f"[SoundDeviceAudioInput] Error in audio processing loop: {e}")
                continue

        print("[SoundDeviceAudioInput] Audio processing thread stopped")

    def _cleanup_resources(self) -> None:
        """Clean up queue and thread resources."""
        # Stop processing thread
        if self._processing_thread and self._processing_thread.is_alive():
            self._stop_processing.set()
            self._processing_thread.join(timeout=2.0)

        # Clear resources
        self._processing_thread = None
        self._audio_queue = None
        self._stream = None
        self._callback = None

    def stop_capture(self) -> None:
        """Stop audio capture."""
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
                print("[SoundDeviceAudioInput] Stopped audio capture")
            except Exception as e:
                print(f"[SoundDeviceAudioInput] Error stopping capture: {e}")
            finally:
                self._cleanup_resources()

    def is_capturing(self) -> bool:
        """Check if currently capturing audio."""
        return self._stream is not None and self._stream.active

    def is_available(self) -> bool:
        """Check if audio input is available."""
        if not self.sd:
            return False

        try:
            devices = self.sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            return len(input_devices) > 0
        except Exception:
            return False

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop_capture()

    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current input device."""
        if not self.sd:
            return None

        try:
            device_info = self.sd.query_devices(kind='input')
            return {
                'name': device_info['name'],
                'channels': device_info['max_input_channels'],
                'sample_rate': device_info['default_samplerate'],
                'driver': 'sounddevice'
            }
        except Exception:
            return None
