# Audio Pipeline Decoupling

This document describes the decoupled audio pipeline implementation that separates audio capture, buffering, and recognition into distinct stages with well-defined interfaces.

## Overview

The audio pipeline consists of three main stages:

1. **Audio Capture Stage** - Captures audio data using an `AudioInputSource`
2. **Audio Buffering Stage** - Buffers audio chunks before processing
3. **Recognition Stage** - Performs voice recognition using a `VoiceRecognitionSource`

These stages communicate via async queues and are coordinated by an `AudioPipelineCoordinator`.

## Architecture

```
┌─────────────────┐    Queue    ┌─────────────────┐    Queue    ┌─────────────────┐
│ AudioCapture    │ ────────→   │ AudioBuffering  │ ────────→   │ Recognition     │
│ Stage           │             │ Stage           │             │ Stage           │
└─────────────────┘             └─────────────────┘             └─────────────────┘
         │                               │                               │
         ▼                               ▼                               ▼
┌─────────────────┐             ┌─────────────────┐             ┌─────────────────┐
│ AudioInputSource│             │ Internal Buffer │             │VoiceRecognition │
│ (interface)     │             │ Management      │             │Source (interface)│
└─────────────────┘             └─────────────────┘             └─────────────────┘
```

## Key Features

### 1. Modular Design
- Each stage can be developed, tested, and maintained independently
- Clear separation of concerns between audio capture, buffering, and recognition
- Easy to swap implementations (e.g., different audio sources or recognition engines)

### 2. Queue-Based Communication
- Async queues provide loose coupling between stages
- Non-blocking data flow prevents bottlenecks
- Configurable queue sizes for different performance requirements

### 3. Interface Compatibility
- Uses existing `AudioInputSource` and `VoiceRecognitionSource` interfaces
- Maintains backward compatibility with current system
- Can be enabled/disabled without code changes

### 4. Testability
- Each stage can be unit tested in isolation
- Mock implementations available for testing
- End-to-end integration tests validate full pipeline

## Usage

### Basic Pipeline Usage

```python
from voice_typing.pipeline import AudioPipelineCoordinator, SoundDeviceAudioInput
from voice_typing.recognition_sources import VoskRecognitionSource

# Create components
audio_input = SoundDeviceAudioInput()
recognition_source = VoskRecognitionSource()

def on_text_recognized(text: str):
    print(f"Recognized: {text}")

# Create and configure pipeline
coordinator = AudioPipelineCoordinator(
    audio_input, 
    recognition_source, 
    on_text_recognized
)

# Initialize and start
config = {
    'sample_rate': 16000,
    'channels': 1,
    'buffer_size': 10,
    'queue_size': 100
}

await coordinator.initialize(config)
await coordinator.start_pipeline()

# Pipeline is now running...

# Stop and cleanup
await coordinator.stop_pipeline() 
await coordinator.cleanup()
```

### Integration with Existing System

```python
from voice_typing import PipelineVoiceTyping, Config, GlobalState, TrayIconManager

# Use pipeline-based voice typing
config = Config()
state_ref = GlobalState()
tray_manager = TrayIconManager(state_ref, None, lambda: None)

voice_typing = PipelineVoiceTyping(config, state_ref, tray_manager)
voice_typing.voice_typing_loop()  # Runs with pipeline system
```

## Pipeline Stages

### AudioCaptureStage
- **Purpose**: Capture audio data from input source
- **Input**: None (first stage)
- **Output**: Raw audio chunks via queue
- **Configuration**: Audio format, sample rate, block size

### AudioBufferingStage  
- **Purpose**: Buffer audio chunks to optimize processing
- **Input**: Audio chunks from capture stage
- **Output**: Audio buffers (collections of chunks) via queue
- **Configuration**: Buffer size, flush timing

### RecognitionStage
- **Purpose**: Perform voice recognition on audio buffers
- **Input**: Audio buffers from buffering stage  
- **Output**: Recognized text via callback
- **Configuration**: Recognition engine settings

## Configuration

The pipeline accepts a configuration dictionary with these options:

```python
config = {
    # Audio format
    'sample_rate': 16000,    # Audio sample rate (Hz)
    'channels': 1,           # Number of audio channels
    'block_size': 8000,      # Audio block size (samples)
    'dtype': 'int16',        # Audio data type
    
    # Pipeline settings
    'buffer_size': 10,       # Number of chunks per buffer
    'queue_size': 100,       # Maximum queue size between stages
    
    # Recognition settings (passed to recognition source)
    # ... recognition-specific config ...
}
```

## Testing

### Running Pipeline Tests

```bash
# Run all pipeline tests
python -m pytest tests/test_audio_pipeline.py -v

# Run integration tests
python -m pytest tests/test_pipeline_integration.py -v

# Run demo
python demo_pipeline.py
```

### Test Structure

- **Unit Tests**: Test each stage individually with mock dependencies
- **Integration Tests**: Test pipeline integration with existing system
- **End-to-End Tests**: Test full pipeline coordinator functionality

## Performance Considerations

### Queue Sizing
- Larger queues provide more buffering but use more memory
- Smaller queues reduce latency but may cause blocking

### Buffer Management
- Larger buffers provide more context for recognition but increase latency
- Smaller buffers reduce latency but may reduce recognition accuracy

### Threading
- Pipeline runs in separate thread with async event loop
- Avoids blocking main application thread
- Clean shutdown handling prevents resource leaks

## Backward Compatibility

The pipeline system maintains full backward compatibility:

- Existing `VoiceTyping` class continues to work unchanged
- New `PipelineVoiceTyping` provides pipeline-based alternative
- Same interfaces and configuration options
- No breaking changes to existing code

## Future Enhancements

The modular design enables future enhancements:

1. **Additional Stages**: Add preprocessing, filtering, or post-processing stages
2. **Multiple Recognition Engines**: Run multiple recognition sources in parallel
3. **Streaming Support**: Add support for continuous streaming recognition
4. **Performance Monitoring**: Add metrics and monitoring for each stage
5. **Configuration Hot-Reloading**: Dynamic reconfiguration without restart

## Implementation Details

### Error Handling
- Each stage handles errors gracefully without affecting other stages
- Failed stages can be restarted independently
- Error propagation through coordinator for centralized handling

### Resource Management
- Proper cleanup of async resources (tasks, queues)
- Safe shutdown procedures for all stages
- Memory-efficient queue management

### Thread Safety
- Async-safe communication between threads
- Thread-safe queue operations
- Proper event loop management

This implementation successfully decouples the audio pipeline while maintaining compatibility and enabling future extensibility.