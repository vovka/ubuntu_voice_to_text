"""
Tests for the audio pipeline decoupling functionality.

Tests the pipeline stages and coordinator to ensure proper separation
of audio capture, buffering, and recognition.
"""

import asyncio
import pytest
from typing import Dict, Any, Optional, Callable, List
from unittest.mock import Mock, MagicMock

from voice_typing.pipeline import (
    AudioPipelineStage,
    PipelineCoordinator,
    AudioCaptureStage,
    AudioBufferingStage,
    RecognitionStage,
    AudioPipelineCoordinator,
)
from voice_typing.interfaces import AudioInputSource, VoiceRecognitionSource


class MockAudioInput(AudioInputSource):
    """Mock audio input for testing."""
    
    def __init__(self):
        self._initialized = False
        self._capturing = False
        self._callback: Optional[Callable[[bytes], None]] = None
        self._simulate_audio_data = []

    def initialize(self, config: Dict[str, Any]) -> bool:
        self._initialized = True
        return True

    def start_capture(self, callback: Callable[[bytes], None]) -> bool:
        if not self._initialized:
            return False
        self._callback = callback
        self._capturing = True
        return True

    def stop_capture(self) -> None:
        self._capturing = False
        self._callback = None

    def is_capturing(self) -> bool:
        return self._capturing

    def is_available(self) -> bool:
        return True

    def cleanup(self) -> None:
        self.stop_capture()
        self._initialized = False

    def get_device_info(self) -> Optional[Dict[str, Any]]:
        return {'name': 'Mock Device', 'channels': 1}

    def simulate_audio_chunk(self, audio_data: bytes) -> None:
        """Simulate receiving audio data."""
        if self._callback and self._capturing:
            self._callback(audio_data)


class MockRecognitionSource(VoiceRecognitionSource):
    """Mock recognition source for testing."""
    
    def __init__(self):
        self._initialized = False
        self._chunks = []
        self._results = []

    def initialize(self, config: Dict[str, Any]) -> bool:
        self._initialized = True
        return True

    def process_audio_chunk(self, audio_chunk: bytes) -> None:
        if self._initialized:
            self._chunks.append(audio_chunk)
            # Simulate recognition result after processing a few chunks
            if len(self._chunks) >= 3:
                self._results.append({
                    'text': f'recognized_text_{len(self._results)}',
                    'confidence': 0.9,
                    'final': True
                })

    def get_result(self) -> Optional[Dict[str, Any]]:
        return self._results.pop(0) if self._results else None

    def is_available(self) -> bool:
        return self._initialized

    def cleanup(self) -> None:
        self._chunks.clear()
        self._results.clear()
        self._initialized = False


@pytest.mark.asyncio
async def test_audio_capture_stage():
    """Test the audio capture pipeline stage."""
    mock_audio = MockAudioInput()
    stage = AudioCaptureStage(mock_audio)
    
    # Test initialization
    config = {'sample_rate': 16000, 'channels': 1}
    assert await stage.initialize(config) == True
    
    # Set up output queue
    output_queue = asyncio.Queue()
    stage.set_output_queue(output_queue)
    
    # Test starting
    assert await stage.start() == True
    assert stage.is_running() == True
    
    # Simulate audio data
    test_data = b'test_audio_chunk'
    mock_audio.simulate_audio_chunk(test_data)
    
    # Wait a bit for async processing
    await asyncio.sleep(0.1)
    
    # Check that data was put in output queue
    assert not output_queue.empty()
    received_data = await output_queue.get()
    assert received_data == test_data
    
    # Test stopping
    await stage.stop()
    assert stage.is_running() == False
    
    # Test cleanup
    await stage.cleanup()


@pytest.mark.asyncio
async def test_audio_buffering_stage():
    """Test the audio buffering pipeline stage."""
    stage = AudioBufferingStage(buffer_size=2)
    
    # Test initialization
    config = {'buffer_size': 2}
    assert await stage.initialize(config) == True
    
    # Set up input and output queues
    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()
    stage.set_input_queue(input_queue)
    stage.set_output_queue(output_queue)
    
    # Test starting
    assert await stage.start() == True
    assert stage.is_running() == True
    
    # Put audio chunks in input queue
    await input_queue.put(b'chunk1')
    await input_queue.put(b'chunk2')
    
    # Wait for buffering
    await asyncio.sleep(0.2)
    
    # Check that buffer was flushed to output queue
    assert not output_queue.empty()
    buffer = await output_queue.get()
    assert len(buffer) == 2
    assert buffer[0] == b'chunk1'
    assert buffer[1] == b'chunk2'
    
    # Test stopping
    await stage.stop()
    assert stage.is_running() == False
    
    # Test cleanup
    await stage.cleanup()


@pytest.mark.asyncio
async def test_recognition_stage():
    """Test the recognition pipeline stage."""
    mock_recognition = MockRecognitionSource()
    recognized_texts = []
    
    def output_callback(text: str):
        recognized_texts.append(text)
    
    stage = RecognitionStage(mock_recognition, output_callback)
    
    # Test initialization
    config = {'sample_rate': 16000}
    assert await stage.initialize(config) == True
    
    # Set up input queue
    input_queue = asyncio.Queue()
    stage.set_input_queue(input_queue)
    
    # Test starting
    assert await stage.start() == True
    assert stage.is_running() == True
    
    # Put audio buffer in input queue
    audio_buffer = [b'chunk1', b'chunk2', b'chunk3']
    await input_queue.put(audio_buffer)
    
    # Wait for recognition processing
    await asyncio.sleep(0.2)
    
    # Check that text was recognized and callback was called
    assert len(recognized_texts) == 1
    assert recognized_texts[0] == 'recognized_text_0'
    
    # Test stopping
    await stage.stop()
    assert stage.is_running() == False
    
    # Test cleanup
    await stage.cleanup()


@pytest.mark.asyncio
async def test_pipeline_coordinator():
    """Test the full pipeline coordinator end-to-end."""
    mock_audio = MockAudioInput()
    mock_recognition = MockRecognitionSource()
    recognized_texts = []
    
    def output_callback(text: str):
        recognized_texts.append(text)
    
    coordinator = AudioPipelineCoordinator(
        mock_audio, mock_recognition, output_callback
    )
    
    # Test initialization
    config = {
        'sample_rate': 16000,
        'channels': 1,
        'buffer_size': 2,
        'queue_size': 10
    }
    assert await coordinator.initialize(config) == True
    
    # Test starting pipeline
    assert await coordinator.start_pipeline() == True
    assert coordinator.is_pipeline_running() == True
    
    # Check stage status
    status = coordinator.get_stage_status()
    assert status['capture'] == True
    assert status['buffering'] == True
    assert status['recognition'] == True
    
    # Simulate audio data flowing through pipeline
    for i in range(6):  # Send enough chunks to trigger recognition
        mock_audio.simulate_audio_chunk(f'audio_chunk_{i}'.encode())
        await asyncio.sleep(0.05)  # Small delay between chunks
    
    # Wait for pipeline processing
    await asyncio.sleep(0.5)
    
    # Check that text was recognized through the entire pipeline
    assert len(recognized_texts) >= 1
    assert 'recognized_text' in recognized_texts[0]
    
    # Test stopping pipeline
    await coordinator.stop_pipeline()
    assert coordinator.is_pipeline_running() == False
    
    # Test cleanup
    await coordinator.cleanup()


def test_pipeline_interfaces_exist():
    """Test that all pipeline interfaces are properly defined."""
    # Test that pipeline classes can be imported
    from voice_typing.pipeline import (
        AudioPipelineStage,
        PipelineCoordinator,
        AudioCaptureStage,
        AudioBufferingStage,
        RecognitionStage,
        AudioPipelineCoordinator,
    )
    
    # Test that they are abstract/concrete as expected
    assert AudioPipelineStage.__abstractmethods__
    assert PipelineCoordinator.__abstractmethods__
    assert len(getattr(AudioCaptureStage, '__abstractmethods__', set())) == 0
    assert len(getattr(AudioBufferingStage, '__abstractmethods__', set())) == 0
    assert len(getattr(RecognitionStage, '__abstractmethods__', set())) == 0
    assert len(getattr(AudioPipelineCoordinator, '__abstractmethods__', set())) == 0


if __name__ == "__main__":
    # Run a simple test to verify the pipeline works
    async def main():
        print("Running pipeline test...")
        await test_pipeline_coordinator()
        print("Pipeline test completed successfully!")
    
    asyncio.run(main())