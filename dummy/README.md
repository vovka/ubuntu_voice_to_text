# Dummy Implementations

This directory contains dummy implementations of all interfaces defined in the architecture for testing and integration verification.

## Overview

The dummy implementations are designed to:
- **Log activity**: Each implementation uses proper logging to show when methods are called and queues are processed
- **Demonstrate queue interaction**: All implementations periodically interact with their queues to show message flow
- **Validate interfaces**: Ensure all interface contracts are properly implemented
- **Enable integration testing**: Allow testing of the application wiring before real implementations are created
- **Support inter-unit communication**: Accept external queue instances to enable shared communication channels between units

## Available Dummy Implementations

### Core Unit Implementations

1. **DummySharedState** (`dummy_shared_state.py`)
   - Implements `ISharedState` interface
   - Manages a state queue and logs state change events
   - Periodically generates test state events
   - Accepts external `state_queue` parameter for shared communication

2. **DummyTrayControl** (`dummy_tray_control.py`)
   - Implements `ITrayControl` interface
   - Processes tray control commands from input queue
   - Simulates tray icon functionality
   - Accepts external `input_queue` parameter for receiving commands

3. **DummyKeyboardListener** (`dummy_keyboard_listener.py`)
   - Implements `IKeyboardListener` interface
   - Simulates hotkey detection and publishes events
   - Generates test keyboard events periodically
   - Accepts external `output_queue` parameter for publishing events

4. **DummySoundRecorder** (`dummy_sound_recorder.py`)
   - Implements `ISoundRecorder` interface
   - Processes control commands and simulates audio recording
   - Manages recording state and generates test audio chunks
   - Accepts external `audio_output_queue` and `control_queue` parameters

5. **DummyNoiseCancelling** (`dummy_noise_cancelling.py`)
   - Implements `INoiseCancelling` interface
   - Processes raw audio and outputs "cleaned" audio
   - Demonstrates audio preprocessing pipeline
   - Accepts external `audio_input_queue` and `audio_output_queue` parameters

6. **DummyVoiceRecognition** (`dummy_voice_recognition.py`)
   - Implements `IVoiceRecognition` interface
   - Converts audio input to recognized text
   - Simulates speech recognition processing
   - Accepts external `audio_input_queue` and `text_output_queue` parameters

7. **DummyOutputHandler** (`dummy_output_handler.py`)
   - Implements `IOutputHandler` interface
   - Processes recognized text for output delivery
   - Simulates clipboard, active window, or file output
   - Accepts external `input_queue` parameter for receiving text

## Usage

### Basic Usage (Individual Units)

```python
import asyncio
from dummy import DummySharedState, DummyTrayControl

# Create dummy implementations with default queues
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

### Inter-Unit Communication via Shared Queues

```python
import asyncio
from dummy import *

async def wired_demo():
    # Create shared queues for inter-unit communication
    keyboard_to_sound = asyncio.Queue()
    sound_to_noise = asyncio.Queue()
    noise_to_voice = asyncio.Queue()
    voice_to_output = asyncio.Queue()
    state_updates = asyncio.Queue()
    
    # Create dummy units with shared queues
    keyboard_listener = DummyKeyboardListener(output_queue=keyboard_to_sound)
    sound_recorder = DummySoundRecorder(
        control_queue=keyboard_to_sound,
        audio_output_queue=sound_to_noise
    )
    noise_cancelling = DummyNoiseCancelling(
        audio_input_queue=sound_to_noise,
        audio_output_queue=noise_to_voice
    )
    voice_recognition = DummyVoiceRecognition(
        audio_input_queue=noise_to_voice,
        text_output_queue=voice_to_output
    )
    output_handler = DummyOutputHandler(input_queue=voice_to_output)
    shared_state = DummySharedState(state_queue=state_updates)
    
    # Run all units concurrently
    tasks = [asyncio.create_task(unit.run()) for unit in [
        keyboard_listener, sound_recorder, noise_cancelling,
        voice_recognition, output_handler, shared_state
    ]]
    
    # Let them demonstrate inter-unit communication
    await asyncio.sleep(10)
    
    # Clean shutdown
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

asyncio.run(wired_demo())
```

### Testing Integration

```python
from dummy import *
import asyncio

async def test_integration():
    # Create all dummy units with default queues
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

All dummy implementations accept an optional configuration dictionary and external queue parameters:

```python
# Configuration example
config = {
    "sample_rate": 44100,
    "output_type": "clipboard",
    "tray_style": "gnome"
}

# With external queues for inter-unit communication
shared_queue = asyncio.Queue()
sound_recorder = DummySoundRecorder(
    config=config,
    audio_output_queue=shared_queue,
    control_queue=asyncio.Queue()
)
```

## External Queue Parameters

Each dummy implementation accepts external queue parameters to enable inter-unit communication:

- **DummySharedState**: `state_queue` - for state change events
- **DummyTrayControl**: `input_queue` - for tray control commands
- **DummyKeyboardListener**: `output_queue` - for publishing hotkey events
- **DummySoundRecorder**: `audio_output_queue`, `control_queue` - for audio chunks and control commands
- **DummyNoiseCancelling**: `audio_input_queue`, `audio_output_queue` - for audio processing pipeline
- **DummyVoiceRecognition**: `audio_input_queue`, `text_output_queue` - for speech recognition pipeline
- **DummyOutputHandler**: `input_queue` - for receiving recognized text

When external queues are provided, the logging will show the queue ID to help track inter-unit communication.

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
- **Shared queues**: When external queues are provided, units communicate through shared channels

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
- External queue parameter tests

## Development

When adding new dummy implementations:

1. Create a new file in the `dummy/` directory
2. Implement the corresponding interface
3. Add comprehensive logging
4. Include queue interaction demonstrations
5. Support external queue parameters for inter-unit communication
6. Add the new class to `__init__.py`
7. Create corresponding unit tests