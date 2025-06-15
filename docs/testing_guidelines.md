# Testing Guidelines and Patterns

This document describes the testing patterns and mock usage for the Ubuntu Voice-to-Text system.

## Overview

The voice typing system provides centralized mock implementations for all major interfaces to enable isolated unit testing. This ensures that:

- Each module can be tested in isolation
- Tests are reliable and repeatable
- External dependencies don't affect test results
- Interface contracts are validated

## Mock Library

### Location

All mock implementations are centralized in:
- `voice_typing/testing/mocks.py` - Mock class implementations
- `voice_typing/testing/__init__.py` - Public API for importing mocks

### Available Mocks

#### MockAudioInputSource

Mock implementation of the `AudioInputSource` interface.

```python
from voice_typing.testing import MockAudioInputSource

# Create mock
audio_input = MockAudioInputSource()

# Initialize
audio_input.initialize({'sample_rate': 16000})

# Set up capture callback
def audio_callback(chunk: bytes):
    print(f"Received audio: {len(chunk)} bytes")

audio_input.start_capture(audio_callback)

# Simulate audio data
audio_input.simulate_audio_chunk(b'test_audio_data')

# Clean up
audio_input.cleanup()
```

**Test Helper Methods:**
- `simulate_audio_chunk(data: bytes)` - Inject audio data into the capture pipeline

#### MockVoiceRecognitionSource

Mock implementation of the `VoiceRecognitionSource` interface.

```python
from voice_typing.testing import MockVoiceRecognitionSource

# Create mock
recognition = MockVoiceRecognitionSource()

# Initialize
recognition.initialize({})

# Process audio chunks
for i in range(4):  # Need 3+ chunks to trigger result
    recognition.process_audio_chunk(f'chunk_{i}'.encode())

# Get recognition result
result = recognition.get_result()
# Returns: {'text': 'hello world', 'confidence': 0.95, 'final': True}
```

**Test Helper Methods:**
- `set_recognition_results(results: List[Dict])` - Set custom recognition results
- `add_pending_result(result: Dict)` - Add result to pending queue

#### MockOutputActionTarget

Mock implementation of the `OutputActionTarget` interface.

```python
from voice_typing.testing import MockOutputActionTarget
from voice_typing.interfaces import OutputType

# Create mock
output = MockOutputActionTarget(OutputType.KEYBOARD)

# Initialize
output.initialize({})

# Deliver text
output.deliver_text("hello world", {'confidence': 0.9})

# Check delivered texts
delivered = output.get_delivered_texts()
# Returns: [("hello world", {'confidence': 0.9})]
```

**Test Helper Methods:**
- `get_delivered_texts()` - Get all delivered text/metadata pairs
- `clear_delivered_texts()` - Clear delivered text history
- `set_supports_formatting(supports: bool)` - Set formatting support flag

#### MockStateManager

Mock implementation of the `StateManager` interface.

```python
from voice_typing.testing import MockStateManager
from voice_typing.interfaces import VoiceTypingState

# Create mock
state_mgr = MockStateManager()

# Check initial state
assert state_mgr.get_current_state() == VoiceTypingState.IDLE

# Change state
state_mgr.set_state(VoiceTypingState.LISTENING, {'source': 'hotkey'})

# Set up state listener
def state_listener(transition):
    print(f"State changed: {transition.from_state} -> {transition.to_state}")

state_mgr.register_state_listener(state_listener)

# Get state history
history = state_mgr.get_state_history()
```

**Test Helper Methods:**
- `clear_listeners()` - Clear all registered listeners
- `get_listener_count()` - Get number of registered listeners

## Testing Patterns

### 1. Isolated Unit Tests

Test individual modules in isolation using mocks for dependencies:

```python
def test_my_module():
    """Test MyModule in isolation."""
    from voice_typing.testing import MockAudioInputSource, MockOutputActionTarget
    from voice_typing.my_module import MyModule
    
    # Create mocks
    audio_input = MockAudioInputSource()
    output_target = MockOutputActionTarget()
    
    # Initialize module with mocks
    module = MyModule(audio_input, output_target)
    
    # Test module behavior
    module.process_audio()
    
    # Verify interactions with mocks
    delivered = output_target.get_delivered_texts()
    assert len(delivered) > 0
```

### 2. Interface Contract Validation

Ensure implementations properly follow interface contracts:

```python
def test_interface_contract():
    """Test that mock follows interface contract."""
    from voice_typing.testing import MockAudioInputSource
    from voice_typing.interfaces import AudioInputSource
    
    # Create mock
    mock = MockAudioInputSource()
    
    # Verify it implements the interface
    assert isinstance(mock, AudioInputSource)
    
    # Test abstract methods are implemented
    assert hasattr(mock, 'initialize')
    assert hasattr(mock, 'start_capture')
    # ... etc
```

### 3. State Transition Testing

Test state management using MockStateManager:

```python
def test_state_transitions():
    """Test valid state transitions."""
    from voice_typing.testing import MockStateManager
    from voice_typing.interfaces import VoiceTypingState
    
    state_mgr = MockStateManager()
    
    # Test valid transition
    assert state_mgr.set_state(VoiceTypingState.LISTENING) == True
    assert state_mgr.get_current_state() == VoiceTypingState.LISTENING
    
    # Test transition history
    history = state_mgr.get_state_history()
    assert len(history) == 1
    assert history[0].to_state == VoiceTypingState.LISTENING
```

### 4. Audio Pipeline Testing

Test audio processing pipelines:

```python
def test_audio_pipeline():
    """Test audio processing pipeline."""
    from voice_typing.testing import MockAudioInputSource, MockVoiceRecognitionSource
    
    # Create mocks
    audio_input = MockAudioInputSource()
    recognition = MockVoiceRecognitionSource()
    
    # Set up pipeline
    audio_input.initialize({})
    recognition.initialize({})
    
    # Process audio through pipeline
    def audio_callback(chunk: bytes):
        recognition.process_audio_chunk(chunk)
    
    audio_input.start_capture(audio_callback)
    
    # Simulate audio input
    for i in range(4):
        audio_input.simulate_audio_chunk(f'chunk_{i}'.encode())
    
    # Check recognition results
    result = recognition.get_result()
    assert result is not None
    assert 'text' in result
```

## Test Organization

### Test File Structure

```
tests/
├── test_interfaces.py           # Interface definition tests
├── test_audio_pipeline.py       # Pipeline component tests
├── test_pipeline_integration.py # Integration tests
├── test_module_isolation/       # Individual module unit tests
│   ├── test_audio_processor.py
│   ├── test_hotkey_manager.py
│   ├── test_config.py
│   └── ...
└── test_end_to_end.py          # Full system tests
```

### Test Categories

1. **Interface Tests** (`test_interfaces.py`)
   - Validate interface definitions
   - Test mock implementations
   - Verify contract compliance

2. **Unit Tests** (`test_module_isolation/`)
   - Test individual modules in isolation
   - Use mocks for all dependencies
   - Focus on module-specific logic

3. **Integration Tests** (`test_pipeline_integration.py`)
   - Test module interactions
   - Use real implementations where possible
   - Validate data flow between modules

4. **End-to-End Tests** (`test_end_to_end.py`)
   - Test complete system functionality
   - Use minimal mocking
   - Validate user scenarios

## Best Practices

### 1. Mock Setup

- Always initialize mocks before use
- Clean up mocks after tests
- Use descriptive test data

```python
def test_example():
    # Setup
    mock = MockAudioInputSource()
    mock.initialize({'sample_rate': 16000})
    
    try:
        # Test logic here
        pass
    finally:
        # Cleanup
        mock.cleanup()
```

### 2. Test Data

- Use realistic test data
- Include edge cases
- Test error conditions

```python
# Good test data examples
test_audio_chunks = [
    b'realistic_audio_data',
    b'',  # empty chunk
    b'x' * 1024,  # large chunk
]

test_recognition_results = [
    {'text': 'hello world', 'confidence': 0.95, 'final': True},
    {'text': 'partial', 'confidence': 0.5, 'final': False},
    {'text': '', 'confidence': 0.0, 'final': True},  # empty result
]
```

### 3. Assertions

- Test both positive and negative cases
- Verify mock interactions
- Check state changes

```python
def test_with_proper_assertions():
    output = MockOutputActionTarget()
    output.initialize({})
    
    # Test successful delivery
    assert output.deliver_text("test") == True
    
    # Verify the text was delivered
    delivered = output.get_delivered_texts()
    assert len(delivered) == 1
    assert delivered[0][0] == "test"
    
    # Test after cleanup
    output.cleanup()
    assert len(output.get_delivered_texts()) == 0
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_interfaces.py

# Run specific test
python -m pytest tests/test_interfaces.py::test_mock_audio_input_implementation

# Run with verbose output
python -m pytest -v

# Run with coverage
python -m pytest --cov=voice_typing
```

### Test Categories

```bash
# Run only interface tests
python -m pytest tests/test_interfaces.py

# Run only unit tests
python -m pytest tests/test_module_isolation/

# Run only integration tests
python -m pytest tests/test_pipeline_integration.py

# Run end-to-end tests
python -m pytest tests/test_end_to_end.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure `PYTHONPATH` is set correctly
   - Check for circular imports
   - Verify mock classes are properly imported

2. **Mock Behavior**
   - Always initialize mocks before use
   - Remember to call cleanup after tests
   - Check mock state between test methods

3. **Async Tests**
   - Install `pytest-asyncio` for async test support
   - Use `@pytest.mark.asyncio` for async test functions
   - Properly await async mock methods

### Debug Tips

```python
# Add debug output to mocks
mock.set_recognition_results([
    {'text': 'debug output', 'confidence': 1.0, 'final': True}
])

# Check mock state
print(f"Mock state: {mock.get_delivered_texts()}")
print(f"Listeners: {state_mgr.get_listener_count()}")

# Use pytest fixtures for complex setups
@pytest.fixture
def audio_pipeline():
    audio_input = MockAudioInputSource()
    recognition = MockVoiceRecognitionSource()
    
    audio_input.initialize({})
    recognition.initialize({})
    
    yield audio_input, recognition
    
    audio_input.cleanup()
    recognition.cleanup()
```

This testing framework enables comprehensive validation of the voice typing system while maintaining clear separation between components and their dependencies.