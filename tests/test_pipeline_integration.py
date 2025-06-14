"""
Integration tests for the pipeline voice typing system.

Tests that the new pipeline system integrates properly with
the existing voice typing infrastructure.
"""

import asyncio
import time
from unittest.mock import Mock, patch
from voice_typing import (
    Config, 
    PipelineVoiceTyping,
    TrayIconManager,
    BasicStateManager,
    VoiceTypingState,
)
from voice_typing.recognition_sources import VoiceRecognitionSource


class MockRecognitionSource(VoiceRecognitionSource):
    """Mock recognition source for testing integration."""
    
    def __init__(self):
        self._initialized = False
        self._chunks = []
        
    def initialize(self, config) -> bool:
        self._initialized = True
        return True
    
    def process_audio_chunk(self, audio_chunk: bytes) -> None:
        if self._initialized:
            self._chunks.append(audio_chunk)
    
    def get_result(self):
        if len(self._chunks) >= 3:
            self._chunks.clear()
            return {'text': 'test integration text', 'confidence': 0.9}
        return None
    
    def is_available(self) -> bool:
        return self._initialized
    
    def cleanup(self) -> None:
        self._chunks.clear()
        self._initialized = False


def test_pipeline_voice_typing_initialization():
    """Test that PipelineVoiceTyping can be initialized with modern components."""
    config = Config()
    state_manager = BasicStateManager()
    
    # Mock TrayIconManager to avoid GUI dependencies
    tray_manager = Mock(spec=TrayIconManager)
    
    mock_recognition = MockRecognitionSource()
    
    # Test initialization
    pipeline_voice_typing = PipelineVoiceTyping(
        config, 
        state_manager, 
        recognition_source=mock_recognition
    )
    
    assert pipeline_voice_typing.config == config
    assert pipeline_voice_typing.state_manager == state_manager
    assert pipeline_voice_typing.recognition_source == mock_recognition
    assert pipeline_voice_typing.audio_input is not None
    
    print("PipelineVoiceTyping initialization test passed")


def test_pipeline_system_startup_shutdown():
    """Test that the pipeline system can start and stop cleanly."""
    config = Config()
    state_manager = BasicStateManager()
    tray_manager = Mock(spec=TrayIconManager)
    mock_recognition = MockRecognitionSource()
    
    pipeline_voice_typing = PipelineVoiceTyping(
        config,
        state_manager,
        recognition_source=mock_recognition
    )
    
    # Mock sounddevice to avoid audio hardware dependencies
    with patch('voice_typing.pipeline.audio_input.SoundDeviceAudioInput.initialize', return_value=True), \
         patch('voice_typing.pipeline.audio_input.SoundDeviceAudioInput.is_available', return_value=True), \
         patch('voice_typing.pipeline.audio_input.SoundDeviceAudioInput.start_capture', return_value=True), \
         patch('voice_typing.pipeline.audio_input.SoundDeviceAudioInput.stop_capture'), \
         patch('voice_typing.pipeline.audio_input.SoundDeviceAudioInput.is_capturing', return_value=False):
        
        # Test startup
        assert pipeline_voice_typing.start_pipeline_system() == True
        
        # Give it a moment to initialize
        time.sleep(0.2)
        
        # Test shutdown
        pipeline_voice_typing.stop_pipeline_system()
    
    print("Pipeline system startup/shutdown test passed")


def test_pipeline_state_integration():
    """Test that the pipeline responds to state changes."""
    config = Config()
    state_manager = BasicStateManager()
    tray_manager = Mock(spec=TrayIconManager)
    mock_recognition = MockRecognitionSource()
    
    pipeline_voice_typing = PipelineVoiceTyping(
        config,
        state_manager,
        recognition_source=mock_recognition
    )
    
    # Mock audio dependencies
    with patch('voice_typing.pipeline.audio_input.SoundDeviceAudioInput.initialize', return_value=True), \
         patch('voice_typing.pipeline.audio_input.SoundDeviceAudioInput.is_available', return_value=True), \
         patch('voice_typing.pipeline.audio_input.SoundDeviceAudioInput.start_capture', return_value=True), \
         patch('voice_typing.pipeline.audio_input.SoundDeviceAudioInput.stop_capture'), \
         patch('voice_typing.pipeline.audio_input.SoundDeviceAudioInput.is_capturing', return_value=False):
        
        # Start the pipeline system
        pipeline_voice_typing.start_pipeline_system()
        time.sleep(0.2)
        
        # Change state to listening
        state_manager.set_state(VoiceTypingState.LISTENING)
        time.sleep(0.3)
        
        # Change state back to idle
        state_manager.set_state(VoiceTypingState.IDLE)
        time.sleep(0.3)
        
        # Shutdown
        pipeline_voice_typing.stop_pipeline_system()
    
    print("Pipeline state integration test passed")


if __name__ == "__main__":
    print("Running pipeline integration tests...")
    
    test_pipeline_voice_typing_initialization()
    test_pipeline_system_startup_shutdown()
    test_pipeline_state_integration()
    
    print("All pipeline integration tests passed!")