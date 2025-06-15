"""
Unit tests for AudioProcessor class.

Tests the audio processing functionality in isolation using mocks.
"""

import pytest
import sys
import os
import time
from unittest.mock import patch, MagicMock

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def test_audio_processor_initialization_with_defaults():
    """Test AudioProcessor initialization with default dependencies."""
    from voice_typing.audio_processor import AudioProcessor
    from voice_typing.config import Config
    from voice_typing.global_state import GlobalState
    
    # Mock the dependencies to avoid actual system calls
    with patch('voice_typing.audio_processor.RecognitionSourceFactory') as mock_factory, \
         patch('voice_typing.audio_processor.OutputDispatcher') as mock_dispatcher_class, \
         patch('voice_typing.audio_processor.KeyboardOutputActionTarget') as mock_keyboard_class:
        
        # Set up mock recognition source
        mock_recognition_source = MagicMock()
        mock_recognition_source.initialize.return_value = True
        mock_factory.create_recognition_source.return_value = mock_recognition_source
        mock_factory.get_recognition_config.return_value = {}
        
        # Set up mock output dispatcher
        mock_dispatcher = MagicMock()
        mock_dispatcher_class.return_value = mock_dispatcher
        
        # Set up mock keyboard target
        mock_keyboard = MagicMock()
        mock_keyboard.initialize.return_value = True
        mock_keyboard_class.return_value = mock_keyboard
        
        # Create config and state
        config = Config({"recognition_source": "test"})
        state = GlobalState()
        
        # Create AudioProcessor
        processor = AudioProcessor(config, state)
        
        # Verify initialization
        assert processor.state_ref == state
        assert processor.recognition_source == mock_recognition_source
        assert processor.output_dispatcher == mock_dispatcher
        
        # Verify factory was called
        mock_factory.create_recognition_source.assert_called_once_with(config)
        mock_factory.get_recognition_config.assert_called_once_with(config)
        mock_recognition_source.initialize.assert_called_once()
        
        # Verify output dispatcher setup
        mock_dispatcher.initialize.assert_called_once()
        mock_dispatcher.add_target.assert_called_once_with(mock_keyboard)


def test_audio_processor_initialization_with_provided_dependencies():
    """Test AudioProcessor initialization with provided dependencies."""
    from voice_typing.audio_processor import AudioProcessor
    from voice_typing.config import Config
    from voice_typing.global_state import GlobalState
    from voice_typing.testing import MockVoiceRecognitionSource, MockOutputActionTarget
    from voice_typing.interfaces.output_action import OutputDispatcher
    
    # Create mocks
    recognition_source = MockVoiceRecognitionSource()
    output_dispatcher = MagicMock(spec=OutputDispatcher)
    
    # Create config and state
    config = Config({"recognition_source": "test"})
    state = GlobalState()
    
    # Create AudioProcessor with provided dependencies
    processor = AudioProcessor(
        config, 
        state, 
        recognition_source=recognition_source, 
        output_dispatcher=output_dispatcher
    )
    
    # Verify provided dependencies are used
    assert processor.recognition_source == recognition_source
    assert processor.output_dispatcher == output_dispatcher
    assert processor.state_ref == state


def test_audio_processor_initialization_failure():
    """Test AudioProcessor handles recognition source initialization failure."""
    from voice_typing.audio_processor import AudioProcessor
    from voice_typing.config import Config
    from voice_typing.global_state import GlobalState
    
    with patch('voice_typing.audio_processor.RecognitionSourceFactory') as mock_factory, \
         patch('sys.exit') as mock_exit:
        
        # Set up mock recognition source that fails to initialize
        mock_recognition_source = MagicMock()
        mock_recognition_source.initialize.return_value = False
        mock_factory.create_recognition_source.return_value = mock_recognition_source
        mock_factory.get_recognition_config.return_value = {}
        
        config = Config({"recognition_source": "test"})
        state = GlobalState()
        
        # This should trigger sys.exit(1)
        AudioProcessor(config, state)
        
        mock_exit.assert_called_once_with(1)


def test_start_listening():
    """Test start_listening method sets up timing correctly."""
    from voice_typing.audio_processor import AudioProcessor
    from voice_typing.testing import MockVoiceRecognitionSource
    
    # Create processor with mock dependencies
    recognition_source = MockVoiceRecognitionSource()
    output_dispatcher = MagicMock()
    
    processor = AudioProcessor(
        config=MagicMock(),
        state_ref=MagicMock(),
        recognition_source=recognition_source,
        output_dispatcher=output_dispatcher
    )
    
    # Test start_listening
    start_time = time.time()
    processor.start_listening()
    
    # Verify timing is set
    assert processor.listening_started_at is not None
    assert processor.listening_started_at >= start_time
    assert processor.last_text_at is None


def test_process_buffer_with_no_result():
    """Test process_buffer when recognition returns no result."""
    from voice_typing.audio_processor import AudioProcessor
    from voice_typing.testing import MockVoiceRecognitionSource
    from voice_typing.global_state import GlobalState
    
    # Create processor with mock dependencies
    recognition_source = MockVoiceRecognitionSource()
    output_dispatcher = MagicMock()
    state = GlobalState()
    
    processor = AudioProcessor(
        config=MagicMock(),
        state_ref=state,
        recognition_source=recognition_source,
        output_dispatcher=output_dispatcher
    )
    
    # Clear any existing results
    recognition_source.cleanup()
    recognition_source.initialize({})
    
    # Process buffer with no recognition results
    buffer = [b'chunk1', b'chunk2']
    processor.process_buffer(buffer)
    
    # Verify audio was processed but no output was dispatched
    assert len(recognition_source._chunks) == 2
    output_dispatcher.dispatch_text.assert_not_called()


def test_process_buffer_with_text_result():
    """Test process_buffer when recognition returns text result."""
    from voice_typing.audio_processor import AudioProcessor
    from voice_typing.testing import MockVoiceRecognitionSource
    from voice_typing.global_state import GlobalState
    
    # Create processor with mock dependencies
    recognition_source = MockVoiceRecognitionSource()
    output_dispatcher = MagicMock()
    state = GlobalState()
    
    processor = AudioProcessor(
        config=MagicMock(),
        state_ref=state,
        recognition_source=recognition_source,
        output_dispatcher=output_dispatcher
    )
    
    # Set up recognition to return a result
    test_result = {'text': 'hello world', 'confidence': 0.95, 'final': True}
    recognition_source.add_pending_result(test_result)
    
    # Process buffer
    start_time = time.time()
    buffer = [b'chunk1', b'chunk2', b'chunk3']
    processor.process_buffer(buffer)
    
    # Verify text was dispatched
    output_dispatcher.dispatch_text.assert_called_once()
    call_args = output_dispatcher.dispatch_text.call_args
    assert call_args[0][0] == 'hello world'  # First positional argument
    
    # Verify metadata
    metadata = call_args[0][1]  # Second positional argument
    assert metadata['confidence'] == 0.95
    assert metadata['source'] == 'AudioProcessor'
    assert 'timestamp' in metadata
    
    # Verify timing was updated
    assert processor.last_text_at is not None
    assert processor.last_text_at >= start_time


def test_inactivity_timeout_listening_state():
    """Test inactivity timeout in listening state when result is available."""
    from voice_typing.audio_processor import AudioProcessor
    from voice_typing.testing import MockVoiceRecognitionSource
    from voice_typing.global_state import GlobalState
    
    # Create processor with mock dependencies
    recognition_source = MockVoiceRecognitionSource()
    output_dispatcher = MagicMock()
    state = GlobalState()
    state.state = "listening"
    
    processor = AudioProcessor(
        config=MagicMock(),
        state_ref=state,
        recognition_source=recognition_source,
        output_dispatcher=output_dispatcher
    )
    
    # Start listening and simulate time passage
    processor.start_listening()
    processor.listening_started_at = time.time() - 6  # 6 seconds ago
    
    # Add a result so the timeout check code runs
    recognition_source.add_pending_result({'text': '', 'confidence': 0.0, 'final': True})
    
    # Process buffer (this triggers timeout check)
    processor.process_buffer([b'chunk'])
    
    # Verify state was changed to idle due to timeout
    assert state.state == "idle"


def test_finish_listening_timeout():
    """Test timeout in finish_listening state when result is available."""
    from voice_typing.audio_processor import AudioProcessor
    from voice_typing.testing import MockVoiceRecognitionSource
    from voice_typing.global_state import GlobalState
    
    # Create processor with mock dependencies
    recognition_source = MockVoiceRecognitionSource()
    output_dispatcher = MagicMock()
    state = GlobalState()
    state.state = "finish_listening"
    
    processor = AudioProcessor(
        config=MagicMock(),
        state_ref=state,
        recognition_source=recognition_source,
        output_dispatcher=output_dispatcher
    )
    
    # Set last text time to 6 seconds ago
    processor.last_text_at = time.time() - 6
    
    # Add a result so the timeout check code runs
    recognition_source.add_pending_result({'text': '', 'confidence': 0.0, 'final': True})
    
    # Process buffer (this triggers timeout check)
    processor.process_buffer([b'chunk'])
    
    # Verify state was changed to idle due to timeout
    assert state.state == "idle"


def test_no_timeout_when_recent_activity():
    """Test that no timeout occurs when there's recent activity."""
    from voice_typing.audio_processor import AudioProcessor
    from voice_typing.testing import MockVoiceRecognitionSource
    from voice_typing.global_state import GlobalState
    
    # Create processor with mock dependencies
    recognition_source = MockVoiceRecognitionSource()
    output_dispatcher = MagicMock()
    state = GlobalState()
    state.state = "listening"
    
    processor = AudioProcessor(
        config=MagicMock(),
        state_ref=state,
        recognition_source=recognition_source,
        output_dispatcher=output_dispatcher
    )
    
    # Start listening recently
    processor.start_listening()
    processor.listening_started_at = time.time() - 2  # 2 seconds ago (within timeout)
    
    # Process buffer
    processor.process_buffer([])
    
    # Verify state remains listening (no timeout)
    assert state.state == "listening"


def test_inactivity_timeout_with_no_recognition_result():
    """Test inactivity timeout when no recognition result is available (demonstrates the bug)."""
    from voice_typing.audio_processor import AudioProcessor
    from voice_typing.testing import MockVoiceRecognitionSource
    from voice_typing.global_state import GlobalState
    
    # Create processor with mock dependencies
    recognition_source = MockVoiceRecognitionSource()
    output_dispatcher = MagicMock()
    state = GlobalState()
    state.state = "listening"
    
    processor = AudioProcessor(
        config=MagicMock(),
        state_ref=state,
        recognition_source=recognition_source,
        output_dispatcher=output_dispatcher
    )
    
    # Start listening and simulate time passage
    processor.start_listening()
    processor.listening_started_at = time.time() - 6  # 6 seconds ago
    
    # Clear any existing results to ensure get_result() returns None
    recognition_source.cleanup()
    recognition_source.initialize({})
    
    # Process empty buffer (simulates silence/inactivity with no recognition result)
    processor.process_buffer([])
    
    # BUG: State should change to idle due to timeout, but currently doesn't
    # because timeout logic is skipped when get_result() returns None
    assert state.state == "idle", "Should timeout to idle state even without recognition results"


if __name__ == "__main__":
    # Run tests manually if called directly
    test_audio_processor_initialization_with_provided_dependencies()
    test_start_listening()
    test_process_buffer_with_no_result()
    test_process_buffer_with_text_result()
    test_no_timeout_when_recent_activity()
    test_inactivity_timeout_with_no_recognition_result()
    
    print("✅ All AudioProcessor unit tests passed!")