# Recognition Source Interface

The Recognition Source Interface defines the contract for voice recognition backends (Vosk, Whisper, etc.) to enable pluggable recognition engines.

## Interface Contract

### VoiceRecognitionSource (Abstract Base Class)

```python
from voice_typing.recognition_sources import VoiceRecognitionSource

class MyRecognitionSource(VoiceRecognitionSource):
    def initialize(self, config: Dict[str, Any]) -> bool:
        # Initialize recognition engine with config
        pass
    
    def process_audio_chunk(self, audio_chunk: bytes) -> None:
        # Process raw audio data
        pass
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        # Get recognition result
        pass
    
    def is_available(self) -> bool:
        # Check if recognition source is ready
        pass
    
    def cleanup(self) -> None:
        # Clean up recognition resources
        pass
```

## Configuration Parameters

The `initialize()` method expects a configuration dictionary with these parameters:

### Common Parameters
- `sample_rate` (int): Audio sample rate (e.g., 16000)

### Vosk-specific Parameters
- `model_path` (str): Path to Vosk model directory

### Whisper-specific Parameters  
- `api_key` (str): OpenAI API key
- `model` (str): Whisper model name (e.g., "gpt-4o-transcribe")

## Usage Examples

### Custom Recognition Source Implementation

```python
from voice_typing.recognition_sources import VoiceRecognitionSource
from typing import Dict, Any, Optional

class CustomRecognitionSource(VoiceRecognitionSource):
    def __init__(self):
        self._recognizer = None
        self._config = None
        self._result_queue = []
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the recognition engine."""
        try:
            self._config = config
            # Initialize your recognition engine here
            # self._recognizer = MyRecognitionEngine(config)
            return True
        except Exception as e:
            print(f"Failed to initialize recognition: {e}")
            return False
    
    def process_audio_chunk(self, audio_chunk: bytes) -> None:
        """Process audio data."""
        if not self._recognizer:
            return
            
        try:
            # Process the audio chunk
            # result = self._recognizer.process(audio_chunk)
            # if result:
            #     self._result_queue.append(result)
            pass
        except Exception as e:
            print(f"Error processing audio: {e}")
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get recognition result."""
        if not self._result_queue:
            return None
            
        # Return the oldest result
        result = self._result_queue.pop(0)
        return {
            'text': result.get('text', ''),
            'confidence': result.get('confidence', 0.0),
            'alternatives': result.get('alternatives', []),
            'final': result.get('final', True)
        }
    
    def is_available(self) -> bool:
        """Check if recognition is available."""
        return self._recognizer is not None
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self._recognizer:
            # Clean up recognition engine
            # self._recognizer.cleanup()
            self._recognizer = None
        self._result_queue.clear()
```

### Using Existing Recognition Sources

```python
from voice_typing.recognition_sources import VoskRecognitionSource, WhisperRecognitionSource

# Vosk Recognition
vosk_config = {
    'sample_rate': 16000,
    'model_path': '/path/to/vosk-model'
}

vosk_source = VoskRecognitionSource()
if vosk_source.initialize(vosk_config):
    # Process audio chunks
    vosk_source.process_audio_chunk(audio_data)
    
    # Get results
    result = vosk_source.get_result()
    if result:
        print(f"Recognized: {result['text']}")

# Whisper Recognition
whisper_config = {
    'sample_rate': 16000,
    'api_key': 'your-openai-api-key',
    'model': 'gpt-4o-transcribe'
}

whisper_source = WhisperRecognitionSource()
if whisper_source.initialize(whisper_config):
    # Process audio chunks
    whisper_source.process_audio_chunk(audio_data)
    
    # Get results
    result = whisper_source.get_result()
    if result:
        print(f"Recognized: {result['text']}")
```

### AudioProcessor Integration

```python
from voice_typing import AudioProcessor, Config, GlobalState

# Custom recognition source
class MockRecognitionSource(VoiceRecognitionSource):
    def initialize(self, config):
        return True
    
    def process_audio_chunk(self, audio_chunk):
        # Mock processing
        pass
    
    def get_result(self):
        return {"text": "hello world", "confidence": 0.95}
    
    def is_available(self):
        return True
    
    def cleanup(self):
        pass

# Use with AudioProcessor
config = Config()
state_ref = GlobalState()
custom_source = MockRecognitionSource()

audio_processor = AudioProcessor(config, state_ref, custom_source)
```

## Recognition Result Format

The `get_result()` method should return a dictionary with this structure:

```python
{
    'text': str,                    # Recognized text
    'confidence': float,            # Confidence score (0.0 to 1.0)
    'alternatives': List[str],      # Alternative recognition results
    'final': bool,                  # True if this is the final result
    'language': str,                # Detected language (optional)
    'duration': float,              # Audio duration in seconds (optional)
    'timestamp': float              # Recognition timestamp (optional)
}
```

Example:
```python
{
    'text': 'hello world',
    'confidence': 0.95,
    'alternatives': ['yellow world', 'hallow world'],
    'final': True,
    'language': 'en-US',
    'duration': 1.2,
    'timestamp': 1634567890.123
}
```

## Error Handling

- Return `False` from `initialize()` if setup fails
- Handle exceptions in `process_audio_chunk()` gracefully
- Return `None` from `get_result()` when no result is available
- Log errors appropriately for debugging
- Ensure `cleanup()` is safe to call multiple times

## Thread Safety

Recognition sources may be accessed from multiple threads:

```python
import threading

class ThreadSafeRecognitionSource(VoiceRecognitionSource):
    def __init__(self):
        self._lock = threading.Lock()
        self._results = []
    
    def process_audio_chunk(self, audio_chunk: bytes) -> None:
        with self._lock:
            # Process audio safely
            pass
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._results.pop(0) if self._results else None
```

## Streaming vs Batch Processing

Recognition sources can support different processing modes:

### Streaming Mode
- Process audio chunks as they arrive
- Return partial results during processing
- Set `final: False` for intermediate results

### Batch Mode  
- Accumulate audio chunks until processing is complete
- Return only final results
- Set `final: True` for all results

## Testing Recognition Sources

```python
import pytest
from voice_typing.recognition_sources import VoiceRecognitionSource

def test_recognition_source_interface():
    """Test that custom source implements interface correctly."""
    source = MyRecognitionSource()
    
    # Test interface methods exist
    assert hasattr(source, 'initialize')
    assert hasattr(source, 'process_audio_chunk')
    assert hasattr(source, 'get_result')
    assert hasattr(source, 'is_available')
    assert hasattr(source, 'cleanup')
    
    # Test initialization
    config = {'sample_rate': 16000}
    assert source.initialize(config) == True
    
    # Test availability
    assert source.is_available() == True
    
    # Test cleanup
    source.cleanup()  # Should not raise exception
```