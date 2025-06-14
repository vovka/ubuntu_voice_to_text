# Audio Input Interface

The Audio Input Interface abstracts audio capture logic to allow different audio input sources to be used interchangeably.

## Interface Contract

### AudioInputSource (Abstract Base Class)

```python
from voice_typing.interfaces import AudioInputSource

class MyAudioInput(AudioInputSource):
    def initialize(self, config: Dict[str, Any]) -> bool:
        # Setup audio capture with config parameters
        pass
    
    def start_capture(self, callback: Callable[[bytes], None]) -> bool:
        # Start capturing and call callback with audio chunks
        pass
    
    def stop_capture(self) -> None:
        # Stop audio capture
        pass
    
    def is_capturing(self) -> bool:
        # Return True if actively capturing
        pass
    
    def is_available(self) -> bool:
        # Return True if audio input is available
        pass
    
    def cleanup(self) -> None:
        # Clean up resources
        pass
    
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        # Return device information
        pass
```

## Configuration Parameters

The `initialize()` method expects a configuration dictionary with these parameters:

- `sample_rate` (int): Audio sample rate in Hz (e.g., 16000)
- `block_size` (int): Audio block size for processing (e.g., 8000)
- `channels` (int): Number of audio channels (1 for mono, 2 for stereo)
- `dtype` (str): Audio data type ("int16", "float32", etc.)

## Usage Example

```python
from voice_typing.interfaces import AudioInputSource

# Custom implementation
class SoundDeviceAudioInput(AudioInputSource):
    def __init__(self):
        self._stream = None
        self._callback = None
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            import sounddevice as sd
            self.sd = sd
            self.config = config
            return True
        except ImportError:
            return False
    
    def start_capture(self, callback: Callable[[bytes], None]) -> bool:
        if self._stream is not None:
            return False
            
        self._callback = callback
        
        def audio_callback(indata, frames, time, status):
            if self._callback:
                self._callback(bytes(indata))
        
        try:
            self._stream = self.sd.RawInputStream(
                samplerate=self.config['sample_rate'],
                blocksize=self.config['block_size'],
                dtype=self.config['dtype'],
                channels=self.config['channels'],
                callback=audio_callback
            )
            self._stream.start()
            return True
        except Exception as e:
            print(f"Failed to start audio capture: {e}")
            return False
    
    def stop_capture(self) -> None:
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            self._callback = None
    
    def is_capturing(self) -> bool:
        return self._stream is not None and self._stream.active
    
    def is_available(self) -> bool:
        try:
            import sounddevice as sd
            return len(sd.query_devices()) > 0
        except:
            return False
    
    def cleanup(self) -> None:
        self.stop_capture()
    
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        try:
            import sounddevice as sd
            device = sd.query_devices(kind='input')
            return {
                'name': device['name'],
                'channels': device['max_input_channels'],
                'sample_rate': device['default_samplerate']
            }
        except:
            return None

# Usage
config = {
    'sample_rate': 16000,
    'block_size': 8000,
    'channels': 1,
    'dtype': 'int16'
}

audio_input = SoundDeviceAudioInput()
if audio_input.initialize(config):
    def on_audio_chunk(chunk: bytes):
        print(f"Received {len(chunk)} bytes of audio")
    
    audio_input.start_capture(on_audio_chunk)
    # ... do other work ...
    audio_input.stop_capture()
    audio_input.cleanup()
```

## Threading Support

For audio inputs that need to run in separate threads, you can inherit from `ThreadedAudioInputSource`:

```python
from voice_typing.interfaces.audio_input import ThreadedAudioInputSource

class MyThreadedAudioInput(ThreadedAudioInputSource):
    def _capture_loop(self) -> None:
        # Main capture loop running in background thread
        while not self._stop_event.is_set():
            # Capture audio data
            audio_chunk = self._capture_audio_chunk()
            
            # Call callback with captured data
            if self._callback and audio_chunk:
                self._callback(audio_chunk)
            
            # Small delay to prevent busy waiting
            self._stop_event.wait(0.01)
```

## Error Handling

- Return `False` from methods that can fail to indicate failure
- Use try/catch blocks around platform-specific audio operations
- Log errors appropriately for debugging
- Ensure `cleanup()` is always safe to call multiple times

## Device Information

The `get_device_info()` method should return device details like:

```python
{
    'name': 'Built-in Microphone',
    'channels': 1,
    'sample_rate': 44100,
    'driver': 'ALSA'
}
```