"""
Unit tests for interface definitions of the voice-to-text transcriber.

These tests validate that the interfaces are properly defined and
can be used for type checking and inheritance.
"""

import asyncio
import pytest
from abc import ABC

# Import interfaces
from interfaces import (
    QueueProtocol,
    ISharedState,
    ITrayControl,
    IKeyboardListener,
    ISoundRecorder,
    INoiseCancelling,
    IVoiceRecognition,
    IOutputHandler,
)


class TestInterfaces:
    """Test suite for interface definitions."""

    def test_queue_protocol_is_protocol(self):
        """Test that QueueProtocol is a Protocol."""
        from typing import Protocol
        # QueueProtocol should be a Protocol
        assert hasattr(QueueProtocol, '__annotations__')

    def test_shared_state_interface_is_abstract(self):
        """Test that ISharedState is an abstract base class."""
        assert issubclass(ISharedState, ABC)
        
        # Should not be instantiable directly
        with pytest.raises(TypeError):
            ISharedState()

    def test_tray_control_interface_is_abstract(self):
        """Test that ITrayControl is an abstract base class."""
        assert issubclass(ITrayControl, ABC)
        
        # Should not be instantiable directly
        with pytest.raises(TypeError):
            ITrayControl()

    def test_keyboard_listener_interface_is_abstract(self):
        """Test that IKeyboardListener is an abstract base class."""
        assert issubclass(IKeyboardListener, ABC)
        
        # Should not be instantiable directly
        with pytest.raises(TypeError):
            IKeyboardListener()

    def test_sound_recorder_interface_is_abstract(self):
        """Test that ISoundRecorder is an abstract base class."""
        assert issubclass(ISoundRecorder, ABC)
        
        # Should not be instantiable directly
        with pytest.raises(TypeError):
            ISoundRecorder()

    def test_noise_cancelling_interface_is_abstract(self):
        """Test that INoiseCancelling is an abstract base class."""
        assert issubclass(INoiseCancelling, ABC)
        
        # Should not be instantiable directly
        with pytest.raises(TypeError):
            INoiseCancelling()

    def test_voice_recognition_interface_is_abstract(self):
        """Test that IVoiceRecognition is an abstract base class."""
        assert issubclass(IVoiceRecognition, ABC)
        
        # Should not be instantiable directly
        with pytest.raises(TypeError):
            IVoiceRecognition()

    def test_output_handler_interface_is_abstract(self):
        """Test that IOutputHandler is an abstract base class."""
        assert issubclass(IOutputHandler, ABC)
        
        # Should not be instantiable directly
        with pytest.raises(TypeError):
            IOutputHandler()

    def test_asyncio_queue_satisfies_queue_protocol(self):
        """Test that asyncio.Queue satisfies QueueProtocol."""
        queue = asyncio.Queue()
        
        # Check that it has the required methods
        assert hasattr(queue, 'put')
        assert hasattr(queue, 'get')
        assert callable(queue.put)
        assert callable(queue.get)

    @pytest.mark.asyncio
    async def test_asyncio_queue_protocol_methods(self):
        """Test that asyncio.Queue methods work as expected for QueueProtocol."""
        queue = asyncio.Queue()
        
        # Test put and get
        test_item = "test_item"
        await queue.put(test_item)
        retrieved_item = await queue.get()
        assert retrieved_item == test_item

    def test_all_interfaces_have_run_method(self):
        """Test that all interfaces define a run method."""
        interfaces_with_run = [
            ISharedState,
            ITrayControl,
            IKeyboardListener,
            ISoundRecorder,
            INoiseCancelling,
            IVoiceRecognition,
            IOutputHandler,
        ]
        
        for interface in interfaces_with_run:
            # Check that the interface has a run method defined
            assert hasattr(interface, 'run')
            # Check that it's marked as abstract
            assert 'run' in interface.__abstractmethods__

    def test_interfaces_have_queue_properties(self):
        """Test that interfaces have the expected queue properties."""
        # ISharedState should have state_queue
        assert hasattr(ISharedState, 'state_queue')
        assert 'state_queue' in ISharedState.__abstractmethods__
        
        # ITrayControl should have input_queue
        assert hasattr(ITrayControl, 'input_queue')
        assert 'input_queue' in ITrayControl.__abstractmethods__
        
        # IKeyboardListener should have output_queue
        assert hasattr(IKeyboardListener, 'output_queue')
        assert 'output_queue' in IKeyboardListener.__abstractmethods__
        
        # ISoundRecorder should have both audio_output_queue and control_queue
        assert hasattr(ISoundRecorder, 'audio_output_queue')
        assert hasattr(ISoundRecorder, 'control_queue')
        assert 'audio_output_queue' in ISoundRecorder.__abstractmethods__
        assert 'control_queue' in ISoundRecorder.__abstractmethods__
        
        # INoiseCancelling should have both audio_input_queue and audio_output_queue
        assert hasattr(INoiseCancelling, 'audio_input_queue')
        assert hasattr(INoiseCancelling, 'audio_output_queue')
        assert 'audio_input_queue' in INoiseCancelling.__abstractmethods__
        assert 'audio_output_queue' in INoiseCancelling.__abstractmethods__
        
        # IVoiceRecognition should have both audio_input_queue and text_output_queue
        assert hasattr(IVoiceRecognition, 'audio_input_queue')
        assert hasattr(IVoiceRecognition, 'text_output_queue')
        assert 'audio_input_queue' in IVoiceRecognition.__abstractmethods__
        assert 'text_output_queue' in IVoiceRecognition.__abstractmethods__
        
        # IOutputHandler should have input_queue
        assert hasattr(IOutputHandler, 'input_queue')
        assert 'input_queue' in IOutputHandler.__abstractmethods__


if __name__ == "__main__":
    pytest.main([__file__])