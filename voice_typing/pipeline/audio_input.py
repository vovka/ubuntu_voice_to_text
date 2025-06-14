"""
SoundDevice-based audio input implementation for the pipeline.

Provides a concrete implementation of AudioInputSource using sounddevice.
"""

from typing import Dict, Any, Optional, Callable
from ..interfaces import AudioInputSource


class SoundDeviceAudioInput(AudioInputSource):
    """
    Audio input implementation using the sounddevice library.
    
    This provides real audio capture functionality for the voice typing system.
    """

    def __init__(self):
        self._stream = None
        self._callback: Optional[Callable[[bytes], None]] = None
        self._config: Optional[Dict[str, Any]] = None
        self.sd = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize sounddevice with the given configuration."""
        try:
            import sounddevice as sd
            self.sd = sd
            self._config = config
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

        def audio_callback(indata, frames, time, status):
            """Internal callback that converts data and calls user callback."""
            if status:
                print(f"[SoundDeviceAudioInput] Audio callback status: {status}")
            
            if self._callback:
                # Convert numpy array to bytes
                audio_bytes = bytes(indata)
                self._callback(audio_bytes)

        try:
            self._stream = self.sd.RawInputStream(
                samplerate=self._config['sample_rate'],
                blocksize=self._config.get('block_size', 8000),
                dtype=self._config.get('dtype', 'int16'),
                channels=self._config.get('channels', 1),
                callback=audio_callback
            )
            self._stream.start()
            print("[SoundDeviceAudioInput] Started audio capture")
            return True
            
        except Exception as e:
            print(f"[SoundDeviceAudioInput] Failed to start capture: {e}")
            self._stream = None
            return False

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
                self._stream = None
                self._callback = None

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