"""
Simple tests for auto-disable functionality that work without external dependencies.
"""

import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_audio_processor_init_adds_listening_started_at():
    """Test that AudioProcessor.__init__ adds the new listening_started_at attribute."""
    # Mock all the external dependencies
    with patch('os.path.exists', return_value=True), \
         patch('vosk.Model') as mock_model, \
         patch('vosk.KaldiRecognizer') as mock_recognizer:
        
        # Import after patching
        from voice_typing import Config, GlobalState, AudioProcessor
        
        config = Config()
        state = GlobalState()
        
        processor = AudioProcessor(config, state)
        
        # Check that the new attribute exists and is initialized correctly
        assert hasattr(processor, 'listening_started_at')
        assert processor.listening_started_at is None


def test_start_listening_method_exists_and_sets_time():
    """Test that start_listening method exists and sets the listening_started_at time."""
    with patch('os.path.exists', return_value=True), \
         patch('vosk.Model'), \
         patch('vosk.KaldiRecognizer'):
        
        from voice_typing import Config, GlobalState, AudioProcessor
        
        config = Config()
        state = GlobalState()
        
        processor = AudioProcessor(config, state)
        
        # Check method exists
        assert hasattr(processor, 'start_listening')
        assert callable(processor.start_listening)
        
        # Call the method
        start_time = time.time()
        processor.start_listening()
        
        # Check that listening_started_at is set
        assert processor.listening_started_at is not None
        assert processor.listening_started_at >= start_time
        assert processor.last_text_at is None


def test_hotkey_manager_accepts_audio_processor():
    """Test that HotkeyManager constructor accepts audio_processor parameter."""
    from voice_typing import Config, GlobalState, HotkeyManager
    
    config = Config()
    state = GlobalState()
    tray_manager = Mock()
    audio_processor = Mock()
    
    # This should not raise an exception
    hotkey_manager = HotkeyManager(config, state, tray_manager, audio_processor)
    
    # Check that audio_processor is stored
    assert hotkey_manager.audio_processor is audio_processor


def test_hotkey_manager_calls_start_listening_on_state_change():
    """Test that HotkeyManager calls start_listening when state changes to listening."""
    from voice_typing import Config, GlobalState, HotkeyManager
    
    config = Config()
    state = GlobalState()
    tray_manager = Mock()
    audio_processor = Mock()
    
    hotkey_manager = HotkeyManager(config, state, tray_manager, audio_processor)
    
    # Change state to listening
    hotkey_manager.set_state('listening')
    
    # Should call start_listening on audio processor
    audio_processor.start_listening.assert_called_once()
    assert state.state == 'listening'


def test_hotkey_manager_no_error_without_audio_processor():
    """Test that HotkeyManager works without audio_processor (backward compatibility)."""
    from voice_typing import Config, GlobalState, HotkeyManager
    
    config = Config()
    state = GlobalState()
    tray_manager = Mock()
    
    # This should not raise an exception (backward compatibility)
    hotkey_manager = HotkeyManager(config, state, tray_manager)
    
    # Should work without audio_processor
    assert hotkey_manager.audio_processor is None
    
    # Should not fail when setting state
    hotkey_manager.set_state('listening')
    assert state.state == 'listening'


def test_global_state_unchanged():
    """Test that GlobalState class is unchanged."""
    from voice_typing import GlobalState
    
    state = GlobalState()
    
    # Check existing attributes are still there
    assert hasattr(state, 'q')
    assert hasattr(state, 'state')
    assert hasattr(state, 'icon')
    assert hasattr(state, 'current_keys')
    assert state.state == 'idle'