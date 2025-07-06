"""
Unit tests for dummy implementations of the voice-to-text transcriber.

These tests validate that all dummy implementations satisfy their interfaces
and can be instantiated and executed properly.
"""

import asyncio
import pytest
import logging
from unittest.mock import Mock

# Import interfaces
from interfaces import (
    ISharedState,
    ITrayControl,
    IKeyboardListener,
    ISoundRecorder,
    INoiseCancelling,
    IVoiceRecognition,
    IOutputHandler,
)

# Import dummy implementations
from dummy import (
    DummySharedState,
    DummyTrayControl,
    DummyKeyboardListener,
    DummySoundRecorder,
    DummyNoiseCancelling,
    DummyVoiceRecognition,
    DummyOutputHandler,
)


class TestDummyImplementations:
    """Test suite for dummy implementations."""

    def test_dummy_shared_state_implements_interface(self):
        """Test that DummySharedState implements ISharedState."""
        dummy = DummySharedState()
        assert isinstance(dummy, ISharedState)
        assert hasattr(dummy, 'state_queue')
        assert hasattr(dummy, 'run')

    def test_dummy_tray_control_implements_interface(self):
        """Test that DummyTrayControl implements ITrayControl."""
        dummy = DummyTrayControl()
        assert isinstance(dummy, ITrayControl)
        assert hasattr(dummy, 'input_queue')
        assert hasattr(dummy, 'run')

    def test_dummy_keyboard_listener_implements_interface(self):
        """Test that DummyKeyboardListener implements IKeyboardListener."""
        dummy = DummyKeyboardListener()
        assert isinstance(dummy, IKeyboardListener)
        assert hasattr(dummy, 'output_queue')
        assert hasattr(dummy, 'run')

    def test_dummy_sound_recorder_implements_interface(self):
        """Test that DummySoundRecorder implements ISoundRecorder."""
        dummy = DummySoundRecorder()
        assert isinstance(dummy, ISoundRecorder)
        assert hasattr(dummy, 'audio_output_queue')
        assert hasattr(dummy, 'control_queue')
        assert hasattr(dummy, 'run')

    def test_dummy_noise_cancelling_implements_interface(self):
        """Test that DummyNoiseCancelling implements INoiseCancelling."""
        dummy = DummyNoiseCancelling()
        assert isinstance(dummy, INoiseCancelling)
        assert hasattr(dummy, 'audio_input_queue')
        assert hasattr(dummy, 'audio_output_queue')
        assert hasattr(dummy, 'run')

    def test_dummy_voice_recognition_implements_interface(self):
        """Test that DummyVoiceRecognition implements IVoiceRecognition."""
        dummy = DummyVoiceRecognition()
        assert isinstance(dummy, IVoiceRecognition)
        assert hasattr(dummy, 'audio_input_queue')
        assert hasattr(dummy, 'text_output_queue')
        assert hasattr(dummy, 'run')

    def test_dummy_output_handler_implements_interface(self):
        """Test that DummyOutputHandler implements IOutputHandler."""
        dummy = DummyOutputHandler()
        assert isinstance(dummy, IOutputHandler)
        assert hasattr(dummy, 'input_queue')
        assert hasattr(dummy, 'run')

    @pytest.mark.asyncio
    async def test_dummy_shared_state_queue_interaction(self):
        """Test that DummySharedState can put and get from queue."""
        dummy = DummySharedState()
        queue = dummy.state_queue
        
        # Test putting and getting from queue
        test_event = "test_state_change"
        await queue.put(test_event)
        retrieved_event = await queue.get()
        assert retrieved_event == test_event

    @pytest.mark.asyncio
    async def test_dummy_sound_recorder_queue_interaction(self):
        """Test that DummySoundRecorder can interact with both queues."""
        dummy = DummySoundRecorder()
        
        # Test control queue
        control_queue = dummy.control_queue
        await control_queue.put("start_recording")
        command = await control_queue.get()
        assert command == "start_recording"
        
        # Test audio output queue
        audio_queue = dummy.audio_output_queue
        await audio_queue.put("test_audio_chunk")
        audio = await audio_queue.get()
        assert audio == "test_audio_chunk"

    @pytest.mark.asyncio
    async def test_dummy_voice_recognition_queue_interaction(self):
        """Test that DummyVoiceRecognition can interact with both queues."""
        dummy = DummyVoiceRecognition()
        
        # Test audio input queue
        audio_queue = dummy.audio_input_queue
        await audio_queue.put("test_audio_input")
        audio = await audio_queue.get()
        assert audio == "test_audio_input"
        
        # Test text output queue
        text_queue = dummy.text_output_queue
        await text_queue.put("test_recognized_text")
        text = await text_queue.get()
        assert text == "test_recognized_text"

    def test_dummy_implementations_with_config(self):
        """Test that dummy implementations accept configuration."""
        config = {"test_param": "test_value"}
        
        tray = DummyTrayControl(config)
        keyboard = DummyKeyboardListener(config)
        recorder = DummySoundRecorder(config)
        noise_canceller = DummyNoiseCancelling(config)
        voice_recognizer = DummyVoiceRecognition(config)
        output_handler = DummyOutputHandler(config)
        
        # All should be created successfully
        assert tray is not None
        assert keyboard is not None
        assert recorder is not None
        assert noise_canceller is not None
        assert voice_recognizer is not None
        assert output_handler is not None

    @pytest.mark.asyncio
    async def test_dummy_implementations_can_run_briefly(self):
        """Test that all dummy implementations can run briefly without error."""
        dummy_units = [
            DummySharedState(),
            DummyTrayControl(),
            DummyKeyboardListener(),
            DummySoundRecorder(),
            DummyNoiseCancelling(),
            DummyVoiceRecognition(),
            DummyOutputHandler(),
        ]
        
        # Create tasks for all run methods
        tasks = []
        for unit in dummy_units:
            task = asyncio.create_task(unit.run())
            tasks.append(task)
        
        # Let them run briefly
        await asyncio.sleep(0.1)
        
        # Cancel all tasks
        for task in tasks:
            task.cancel()
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete without non-cancellation exceptions
        for result in results:
            if isinstance(result, Exception) and not isinstance(result, asyncio.CancelledError):
                pytest.fail(f"Unexpected exception: {result}")


if __name__ == "__main__":
    pytest.main([__file__])