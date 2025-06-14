# Module Interfaces Documentation

This document describes the formal interfaces defined for the Ubuntu Voice-to-Text application to enable decoupling and modularity.

## Overview

The voice typing system is organized around four main interfaces that define clear contracts between different modules:

1. **Recognition Source Interface** - Handles voice recognition processing
2. **Audio Input Interface** - Manages audio capture from input devices  
3. **Output Action Interface** - Delivers recognized text to various targets
4. **State Manager Interface** - Manages application state and transitions

## Interface Definitions

### Recognition Source Interface

**Location**: `voice_typing/recognition_sources/base.py`  
**Class**: `VoiceRecognitionSource`

Defines the contract for voice recognition backends (Vosk, Whisper, etc.).

**Key Methods**:
- `initialize(config)` - Initialize with configuration
- `process_audio_chunk(audio_chunk)` - Process raw audio data
- `get_result()` - Get recognition results
- `is_available()` - Check if source is ready
- `cleanup()` - Clean up resources

### Audio Input Interface

**Location**: `voice_typing/interfaces/audio_input.py`  
**Class**: `AudioInputSource`

Abstracts audio capture logic for different input sources.

**Key Methods**:
- `initialize(config)` - Setup audio capture parameters
- `start_capture(callback)` - Begin capturing with callback
- `stop_capture()` - Stop audio capture
- `is_capturing()` - Check capture status
- `is_available()` - Check if input is available
- `get_device_info()` - Get input device information

### Output Action Interface

**Location**: `voice_typing/interfaces/output_action.py`  
**Class**: `OutputActionTarget`

Defines how recognized text is delivered to different targets.

**Key Methods**:
- `initialize(config)` - Setup output target
- `deliver_text(text, metadata)` - Send text to target
- `is_available()` - Check if target is ready
- `get_output_type()` - Get the output type
- `supports_formatting()` - Check formatting support

**Supported Output Types**:
- `KEYBOARD` - Type text using keyboard simulation
- `CLIPBOARD` - Copy text to system clipboard
- `FILE` - Write text to file
- `CALLBACK` - Call custom function with text

### State Manager Interface

**Location**: `voice_typing/interfaces/state_manager.py`  
**Class**: `StateManager`

Manages application state transitions and event notifications.

**Key Methods**:
- `get_current_state()` - Get current application state
- `set_state(new_state, metadata)` - Change to new state
- `can_transition_to(new_state)` - Check if transition is valid
- `register_state_listener(callback)` - Listen for state changes
- `get_state_history()` - Get recent state transitions

**States**:
- `IDLE` - Not actively listening
- `LISTENING` - Actively capturing audio
- `FINISH_LISTENING` - Processing captured audio
- `PROCESSING` - Recognition in progress
- `ERROR` - Error condition

## Usage Examples

See individual interface documentation files for detailed usage examples:

- [Recognition Source Interface](recognition_source.md)
- [Audio Input Interface](audio_input.md)
- [Output Action Interface](output_action.md)
- [State Manager Interface](state_manager.md)

## Implementation Guidelines

1. **Interface Compliance**: All implementations must inherit from the abstract base classes
2. **Error Handling**: Methods should return boolean success/failure status where appropriate
3. **Resource Management**: Always implement proper cleanup in `cleanup()` methods
4. **Thread Safety**: Consider thread safety for interfaces used across threads
5. **Configuration**: Use configuration dictionaries for flexible initialization