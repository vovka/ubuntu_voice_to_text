# Output Dispatcher Architecture

## Overview

The Output Dispatcher provides a decoupled architecture for handling recognized text delivery. Instead of recognition logic directly outputting text (e.g., typing with xdotool), the dispatcher acts as an intermediary that can route text to multiple output targets.

## Key Components

### OutputDispatcher

The central component that manages text delivery:

- **Target Management**: Registers and manages multiple output targets
- **Event Distribution**: Delivers recognized text to all registered targets and listeners
- **Error Handling**: Gracefully handles failures in individual targets
- **Metadata Support**: Passes recognition metadata (confidence, timestamp, etc.) to targets

### Output Targets

Implementations of `OutputActionTarget` that handle specific output methods:

- **KeyboardOutputActionTarget**: Types text using keyboard simulation (xdotool)
- **CallbackOutputActionTarget**: Calls custom functions with recognized text
- **MultiOutputActionTarget**: Distributes text to multiple sub-targets
- **Future targets**: Clipboard, file output, network APIs, etc.

## Architecture Benefits

### Decoupling

Recognition logic no longer directly handles output:

```python
# Old approach - direct coupling
def process_audio_result(text):
    subprocess.run(["xdotool", "type", text + " "])

# New approach - via dispatcher
def process_audio_result(text, metadata):
    dispatcher.dispatch_text(text, metadata)
```

### Multiple Output Targets

Single recognition can output to multiple destinations simultaneously:

```python
dispatcher = OutputDispatcher()
dispatcher.add_target(KeyboardOutputActionTarget())
dispatcher.add_target(ClipboardOutputActionTarget())
dispatcher.add_target(FileOutputActionTarget())

# Text goes to keyboard, clipboard, and file
dispatcher.dispatch_text("hello world")
```

### Event-Driven Architecture

Components can subscribe to text events without being output targets:

```python
def log_recognized_text(text, metadata):
    logger.info(f"Recognized: {text} (confidence: {metadata['confidence']})")

dispatcher.add_event_listener(log_recognized_text)
```

## Integration Points

### AudioProcessor

Updated to use OutputDispatcher instead of direct typing:

```python
class AudioProcessor:
    def __init__(self, config, state_ref, recognition_source=None, output_dispatcher=None):
        # Set up output dispatcher with default keyboard target
        if output_dispatcher is None:
            output_dispatcher = OutputDispatcher()
            output_dispatcher.initialize()
            keyboard_target = KeyboardOutputActionTarget()
            if keyboard_target.initialize({}):
                output_dispatcher.add_target(keyboard_target)
        
        self.output_dispatcher = output_dispatcher

    def process_buffer(self, buffer):
        # ... recognition logic ...
        if result.get("text"):
            metadata = {
                'confidence': result.get('confidence', 0.0),
                'timestamp': time.time(),
                'source': 'AudioProcessor'
            }
            self.output_dispatcher.dispatch_text(result["text"], metadata)
```

### PipelineVoiceTyping

Similarly updated to use the dispatcher:

```python
class PipelineVoiceTyping:
    def _text_output_callback(self, text: str) -> None:
        metadata = {
            'confidence': 1.0,
            'timestamp': time.time(),
            'source': 'PipelineVoiceTyping'
        }
        self.output_dispatcher.dispatch_text(text, metadata)
```

## Usage Examples

### Basic Setup

```python
from voice_typing.interfaces.output_action import (
    OutputDispatcher,
    KeyboardOutputActionTarget
)

# Create dispatcher
dispatcher = OutputDispatcher()
dispatcher.initialize()

# Add keyboard output
keyboard_target = KeyboardOutputActionTarget()
keyboard_target.initialize({'append_space': True})
dispatcher.add_target(keyboard_target)

# Use dispatcher
dispatcher.dispatch_text("hello world", {'confidence': 0.95})
```

### Multiple Targets

```python
# Add multiple output targets
clipboard_target = ClipboardOutputActionTarget()
clipboard_target.initialize({})
dispatcher.add_target(clipboard_target)

file_target = FileOutputActionTarget()
file_target.initialize({'target': '/tmp/recognized_text.txt'})
dispatcher.add_target(file_target)

# Text goes to keyboard, clipboard, and file
dispatcher.dispatch_text("recognized speech")
```

### Event Listeners

```python
# Add event listener for logging
def text_logger(text, metadata):
    timestamp = metadata.get('timestamp', time.time())
    confidence = metadata.get('confidence', 0.0)
    source = metadata.get('source', 'unknown')
    print(f"[{timestamp}] {source}: '{text}' (confidence: {confidence:.2f})")

dispatcher.add_event_listener(text_logger)

# Now all dispatched text will be logged
dispatcher.dispatch_text("test message", {'confidence': 0.85})
```

### Custom Output Targets

```python
class NetworkOutputTarget(OutputActionTarget):
    def initialize(self, config):
        self.api_url = config.get('api_url')
        return self.api_url is not None
    
    def deliver_text(self, text, metadata):
        try:
            response = requests.post(self.api_url, json={
                'text': text,
                'metadata': metadata
            })
            return response.status_code == 200
        except:
            return False
    
    def is_available(self):
        return self.api_url is not None
    
    def get_output_type(self):
        return OutputType.CALLBACK  # Or define new type
    
    def supports_formatting(self):
        return False
    
    def cleanup(self):
        pass

# Use custom target
network_target = NetworkOutputTarget()
network_target.initialize({'api_url': 'https://api.example.com/speech'})
dispatcher.add_target(network_target)
```

## Migration from Direct Output

### Before (Coupled)

```python
class AudioProcessor:
    def process_buffer(self, buffer):
        result = self.recognition_source.get_result()
        if result.get("text"):
            self.type_text(result["text"])  # Direct coupling
    
    @staticmethod
    def type_text(text):
        subprocess.run(["xdotool", "type", text + " "])
```

### After (Decoupled)

```python
class AudioProcessor:
    def __init__(self, ..., output_dispatcher=None):
        if output_dispatcher is None:
            output_dispatcher = OutputDispatcher()
            output_dispatcher.initialize()
            keyboard_target = KeyboardOutputActionTarget()
            keyboard_target.initialize({})
            output_dispatcher.add_target(keyboard_target)
        self.output_dispatcher = output_dispatcher
    
    def process_buffer(self, buffer):
        result = self.recognition_source.get_result()
        if result.get("text"):
            metadata = {'confidence': result.get('confidence', 0.0)}
            self.output_dispatcher.dispatch_text(result["text"], metadata)
```

## Testing

The dispatcher architecture enables better testing:

```python
def test_recognition_output():
    # Create test dispatcher
    dispatcher = OutputDispatcher()
    dispatcher.initialize()
    
    # Add test target
    received_texts = []
    def test_callback(text, metadata):
        received_texts.append((text, metadata))
    
    test_target = CallbackOutputActionTarget()
    test_target.initialize({'callback': test_callback})
    dispatcher.add_target(test_target)
    
    # Test audio processor with test dispatcher
    audio_processor = AudioProcessor(config, state_ref, output_dispatcher=dispatcher)
    
    # Verify text delivery without actual keyboard typing
    # ... test logic ...
```

## Error Handling

The dispatcher provides robust error handling:

- **Target Failures**: If one target fails, others continue to receive text
- **Exception Isolation**: Exceptions in targets don't crash recognition
- **Graceful Degradation**: System continues working even if some outputs fail

```python
# Even if keyboard target fails, callback target still works
dispatcher.add_target(failing_keyboard_target)  # May fail
dispatcher.add_target(working_callback_target)  # Still works

# Dispatcher continues delivering to working targets
dispatcher.dispatch_text("test")  # Callback target receives text
```

## Future Enhancements

The dispatcher architecture enables future features:

1. **Configuration-Based Output**: Define output targets in config files
2. **Dynamic Target Management**: Add/remove targets during runtime
3. **Output Filtering**: Route different text types to different targets
4. **Batch Processing**: Collect and deliver text in batches
5. **Priority-Based Delivery**: Deliver to high-priority targets first
6. **Output Transformation**: Modify text before delivery (formatting, translation, etc.)

## Conclusion

The Output Dispatcher successfully decouples recognition logic from output handling, providing:

- **Flexibility**: Support for multiple output targets
- **Testability**: Easy to test without side effects
- **Extensibility**: Simple to add new output methods
- **Reliability**: Graceful error handling and recovery
- **Maintainability**: Clear separation of concerns

This architecture satisfies the requirements of issue #40 by ensuring recognition logic does not output text directly, implementing a documented output dispatcher, and enabling output modules to subscribe to dispatcher events.