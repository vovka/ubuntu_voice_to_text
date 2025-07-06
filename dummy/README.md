# Dummy Implementations

This directory contains dummy implementations of all interfaces defined in the architecture for testing and integration verification.

## Overview

The dummy implementations are designed to:
- **Log activity**: Each implementation uses proper logging to show when methods are called and queues are processed
- **Demonstrate queue interaction**: All implementations periodically interact with their queues to show message flow
- **Validate interfaces**: Ensure all interface contracts are properly implemented
- **Enable integration testing**: Allow testing of the application wiring before real implementations are created

## Available Dummy Implementations

### Core Unit Implementations

1. **DummySharedState** (`dummy_shared_state.py`)
   - Implements `ISharedState` interface
   - Manages a state queue and logs state change events
   - Periodically generates test state events

2. **DummyTrayControl** (`dummy_tray_control.py`)
   - Implements `ITrayControl` interface
   - Processes tray control commands from input queue
   - Simulates tray icon functionality

3. **DummyKeyboardListener** (`dummy_keyboard_listener.py`)
   - Implements `IKeyboardListener` interface
   - Simulates hotkey detection and publishes events
   - Generates test keyboard events periodically

4. **DummySoundRecorder** (`dummy_sound_recorder.py`)
   - Implements `ISoundRecorder` interface
   - Processes control commands and simulates audio recording
   - Manages recording state and generates test audio chunks

5. **DummyNoiseCancelling** (`dummy_noise_cancelling.py`)
   - Implements `INoiseCancelling` interface
   - Processes raw audio and outputs "cleaned" audio
   - Demonstrates audio preprocessing pipeline

6. **DummyVoiceRecognition** (`dummy_voice_recognition.py`)
   - Implements `IVoiceRecognition` interface
   - Converts audio input to recognized text
   - Simulates speech recognition processing

7. **DummyOutputHandler** (`dummy_output_handler.py`)
   - Implements `IOutputHandler` interface
   - Processes recognized text for output delivery
   - Simulates clipboard, active window, or file output

## Usage

### Basic Usage

```python
import asyncio
from dummy import DummySharedState, DummyTrayControl

# Create dummy implementations
shared_state = DummySharedState()
tray_control = DummyTrayControl({"tray_style": "gnome"})

# Run them concurrently
async def main():
    await asyncio.gather(
        shared_state.run(),
        tray_control.run()
    )

asyncio.run(main())
```

### Testing Integration

```python
from dummy import *
import asyncio

async def test_integration():
    # Create all dummy units
    units = [
        DummySharedState(),
        DummyTrayControl(),
        DummyKeyboardListener(),
        DummySoundRecorder(),
        DummyNoiseCancelling(),
        DummyVoiceRecognition(),
        DummyOutputHandler(),
    ]
    
    # Run all units concurrently
    tasks = [asyncio.create_task(unit.run()) for unit in units]
    
    # Let them run for a while
    await asyncio.sleep(5)
    
    # Cancel all tasks
    for task in tasks:
        task.cancel()
    
    await asyncio.gather(*tasks, return_exceptions=True)

asyncio.run(test_integration())
```

## Configuration

All dummy implementations accept an optional configuration dictionary:

```python
config = {
    "sample_rate": 44100,
    "output_type": "clipboard",
    "tray_style": "gnome"
}

sound_recorder = DummySoundRecorder(config)
```

## Logging

All dummy implementations use the Python `logging` module with logger names based on their module path:
- `dummy.dummy_shared_state`
- `dummy.dummy_tray_control`
- `dummy.dummy_keyboard_listener`
- etc.

To see all logging output:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Queue Activity

Each dummy implementation demonstrates different queue interaction patterns:

- **Input queues**: Wait for messages with timeouts, process received messages
- **Output queues**: Generate and send test messages periodically
- **Bidirectional**: Show both input processing and output generation

## Testing

Run the test suite to verify all implementations:

```bash
python -m pytest tests/ -v
```

The test suite includes:
- Interface conformance tests
- Queue interaction tests
- Configuration acceptance tests
- Concurrent execution tests

## Development

When adding new dummy implementations:

1. Create a new file in the `dummy/` directory
2. Implement the corresponding interface
3. Add comprehensive logging
4. Include queue interaction demonstrations
5. Add the new class to `__init__.py`
6. Create corresponding unit tests