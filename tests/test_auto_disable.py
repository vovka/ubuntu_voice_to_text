"""
Tests for auto-disable listening functionality after 5 seconds of inactivity.
"""

import sys
import os
import time
import queue
from unittest.mock import Mock, patch

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest

def test_audio_processor_has_required_attributes():
    """Test that AudioProcessor has the new timing attributes."""
    try:
        from voice_typing import Config, GlobalState, AudioProcessor
        
        config = Config()
        state = GlobalState()
        
        # Mock the vosk model path check since we won't have the model in tests
        with patch('os.path.exists', return_value=True), \
             patch('vosk.Model'), \
             patch('vosk.KaldiRecognizer'):
            processor = AudioProcessor(config, state)
            
            # Check new attributes exist
            assert hasattr(processor, 'listening_started_at')
            assert hasattr(processor, 'start_listening')
            assert processor.listening_started_at is None
            
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_start_listening_resets_timers():
    """Test that start_listening method resets the timers correctly."""
    try:
        from voice_typing import Config, GlobalState, AudioProcessor
        
        config = Config()
        state = GlobalState()
        
        with patch('os.path.exists', return_value=True), \
             patch('vosk.Model'), \
             patch('vosk.KaldiRecognizer'):
            processor = AudioProcessor(config, state)
            
            # Call start_listening
            start_time = time.time()
            processor.start_listening()
            
            # Check that timers are set correctly
            assert processor.listening_started_at is not None
            assert processor.listening_started_at >= start_time
            assert processor.last_text_at is None
            
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_auto_disable_during_listening_no_text():
    """Test auto-disable when listening with no text received."""
    try:
        from voice_typing import Config, GlobalState, AudioProcessor
        
        config = Config()
        state = GlobalState()
        state.state = 'listening'
        
        with patch('os.path.exists', return_value=True), \
             patch('vosk.Model'), \
             patch('vosk.KaldiRecognizer') as mock_recognizer:
            
            # Mock recognizer to return empty result
            mock_recognizer_instance = Mock()
            mock_recognizer_instance.AcceptWaveform.return_value = True
            mock_recognizer_instance.Result.return_value = '{"text": ""}'
            mock_recognizer.return_value = mock_recognizer_instance
            
            processor = AudioProcessor(config, state)
            
            # Start listening 6 seconds ago
            processor.listening_started_at = time.time() - 6
            processor.last_text_at = None
            
            # Process buffer
            processor.process_buffer([b'dummy_audio_data'])
            
            # Should auto-disable after 5 seconds
            assert state.state == 'idle'
            
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_auto_disable_during_listening_with_old_text():
    """Test auto-disable when listening with old text (>5 seconds)."""
    try:
        from voice_typing import Config, GlobalState, AudioProcessor
        
        config = Config()
        state = GlobalState()
        state.state = 'listening'
        
        with patch('os.path.exists', return_value=True), \
             patch('vosk.Model'), \
             patch('vosk.KaldiRecognizer') as mock_recognizer:
            
            # Mock recognizer to return empty result
            mock_recognizer_instance = Mock()
            mock_recognizer_instance.AcceptWaveform.return_value = True
            mock_recognizer_instance.Result.return_value = '{"text": ""}'
            mock_recognizer.return_value = mock_recognizer_instance
            
            processor = AudioProcessor(config, state)
            
            # Start listening and set old text time
            processor.listening_started_at = time.time() - 3
            processor.last_text_at = time.time() - 6  # Text was 6 seconds ago
            
            # Process buffer
            processor.process_buffer([b'dummy_audio_data'])
            
            # Should auto-disable due to old text
            assert state.state == 'idle'
            
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_no_auto_disable_with_recent_text():
    """Test that auto-disable doesn't happen with recent text."""
    try:
        from voice_typing import Config, GlobalState, AudioProcessor
        
        config = Config()
        state = GlobalState()
        state.state = 'listening'
        
        with patch('os.path.exists', return_value=True), \
             patch('vosk.Model'), \
             patch('vosk.KaldiRecognizer') as mock_recognizer:
            
            # Mock recognizer to return empty result
            mock_recognizer_instance = Mock()
            mock_recognizer_instance.AcceptWaveform.return_value = True
            mock_recognizer_instance.Result.return_value = '{"text": ""}'
            mock_recognizer.return_value = mock_recognizer_instance
            
            processor = AudioProcessor(config, state)
            
            # Start listening and set recent text time
            processor.listening_started_at = time.time() - 7
            processor.last_text_at = time.time() - 2  # Text was 2 seconds ago
            
            # Process buffer
            processor.process_buffer([b'dummy_audio_data'])
            
            # Should NOT auto-disable due to recent text
            assert state.state == 'listening'
            
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_hotkey_manager_calls_start_listening():
    """Test that HotkeyManager calls start_listening when state changes to listening."""
    try:
        from voice_typing import Config, GlobalState, HotkeyManager, TrayIconManager
        
        config = Config()
        state = GlobalState()
        
        # Mock dependencies
        tray_manager = Mock()
        audio_processor = Mock()
        
        hotkey_manager = HotkeyManager(config, state, tray_manager, audio_processor)
        
        # Change state to listening
        hotkey_manager.set_state('listening')
        
        # Should call start_listening on audio processor
        audio_processor.start_listening.assert_called_once()
        assert state.state == 'listening'
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_manual_stop_still_works():
    """Test that manual hotkey stop still works correctly."""
    try:
        from voice_typing import Config, GlobalState, HotkeyManager, TrayIconManager
        
        config = Config()
        state = GlobalState()
        state.state = 'listening'
        
        # Mock dependencies
        tray_manager = Mock()
        audio_processor = Mock()
        
        hotkey_manager = HotkeyManager(config, state, tray_manager, audio_processor)
        
        # Simulate hotkey release while listening
        hotkey_manager.set_state('finish_listening')
        
        # Should transition to finish_listening (manual stop)
        assert state.state == 'finish_listening'
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")