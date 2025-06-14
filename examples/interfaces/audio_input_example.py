"""
Example implementation of AudioInputSource using sounddevice.

This demonstrates how to implement the AudioInput interface
for a real audio capture system.
"""

from typing import Dict, Any, Optional, Callable
from voice_typing.interfaces import AudioInputSource


class SoundDeviceAudioInput(AudioInputSource):
    """
    Audio input implementation using the sounddevice library.
    
    This provides real audio capture functionality for the voice typing system.
    """

    def __init__(self):
        self._stream = None
        self._callback = None
        self._config = None
        self.sd = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize sounddevice with the given configuration."""
        try:
            import sounddevice as sd
            self.sd = sd
            self._config = config
            
            # Validate configuration
            required_keys = ['sample_rate', 'block_size', 'channels', 'dtype']
            for key in required_keys:
                if key not in config:
                    print(f"[SoundDeviceAudioInput] Missing required config key: {key}")
                    return False
            
            print(f"[SoundDeviceAudioInput] Initialized with config: {config}")
            return True
            
        except ImportError:
            print("[SoundDeviceAudioInput] sounddevice not available")
            return False
        except Exception as e:
            print(f"[SoundDeviceAudioInput] Initialization error: {e}")
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
                blocksize=self._config['block_size'],
                dtype=self._config['dtype'],
                channels=self._config['channels'],
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
        self._config = None
        self.sd = None

    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current input device."""
        if not self.sd:
            return None
            
        try:
            device = self.sd.query_devices(kind='input')
            return {
                'name': device['name'],
                'channels': device['max_input_channels'],
                'sample_rate': device['default_samplerate'],
                'hostapi': device['hostapi']
            }
        except Exception as e:
            print(f"[SoundDeviceAudioInput] Error getting device info: {e}")
            return None


# Example usage
if __name__ == "__main__":
    import time
    
    def on_audio_chunk(chunk: bytes):
        print(f"Received {len(chunk)} bytes of audio")
    
    # Create and configure audio input
    config = {
        'sample_rate': 16000,
        'block_size': 8000,
        'channels': 1,
        'dtype': 'int16'
    }
    
    audio_input = SoundDeviceAudioInput()
    
    if audio_input.initialize(config):
        print("Audio input initialized successfully")
        
        # Get device info
        device_info = audio_input.get_device_info()
        if device_info:
            print(f"Using device: {device_info}")
        
        # Start capture
        if audio_input.start_capture(on_audio_chunk):
            print("Recording for 5 seconds...")
            time.sleep(5)
            
            # Stop capture
            audio_input.stop_capture()
            print("Recording stopped")
        else:
            print("Failed to start capture")
    else:
        print("Failed to initialize audio input")
    
    # Cleanup
    audio_input.cleanup()