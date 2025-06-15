"""
Tests for the Output Dispatcher functionality.

Validates that the OutputDispatcher properly manages output targets
and delivers text events to subscribers.
"""

import pytest
import sys
import os
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, patch

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def test_output_dispatcher_can_be_imported():
    """Test that OutputDispatcher can be imported."""
    try:
        from voice_typing.interfaces.output_action import OutputDispatcher
        dispatcher = OutputDispatcher()
        assert dispatcher is not None
        print("OutputDispatcher imported successfully")
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_output_dispatcher_initialization():
    """Test OutputDispatcher initialization."""
    try:
        from voice_typing.interfaces.output_action import OutputDispatcher
        
        dispatcher = OutputDispatcher()
        assert not dispatcher.is_initialized()
        
        # Initialize dispatcher
        assert dispatcher.initialize() == True
        assert dispatcher.is_initialized() == True
        
        # Test target count starts at zero
        assert dispatcher.get_target_count() == 0
        
        print("OutputDispatcher initialization works correctly")
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_output_dispatcher_target_management():
    """Test adding and removing targets from OutputDispatcher."""
    try:
        from voice_typing.interfaces.output_action import (
            OutputDispatcher, 
            CallbackOutputActionTarget,
            OutputType
        )
        
        dispatcher = OutputDispatcher()
        dispatcher.initialize()
        
        # Create mock target
        received_calls = []
        def test_callback(text: str, metadata: Optional[Dict[str, Any]]):
            received_calls.append((text, metadata))
        
        target = CallbackOutputActionTarget()
        target.initialize({'callback': test_callback})
        
        # Test adding target
        assert dispatcher.add_target(target) == True
        assert dispatcher.get_target_count() == 1
        
        # Test getting targets by type
        callback_targets = dispatcher.get_targets_by_type(OutputType.CALLBACK)
        assert len(callback_targets) == 1
        assert callback_targets[0] == target
        
        # Test removing target
        assert dispatcher.remove_target(target) == True
        assert dispatcher.get_target_count() == 0
        
        # Test removing non-existent target
        assert dispatcher.remove_target(target) == False
        
        print("OutputDispatcher target management works correctly")
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_output_dispatcher_text_dispatch():
    """Test text dispatching to multiple targets."""
    try:
        from voice_typing.interfaces.output_action import (
            OutputDispatcher,
            CallbackOutputActionTarget
        )
        
        dispatcher = OutputDispatcher()
        dispatcher.initialize()
        
        # Create multiple targets
        calls1 = []
        calls2 = []
        
        def callback1(text, metadata):
            calls1.append((text, metadata))
        
        def callback2(text, metadata):
            calls2.append((text, metadata))
        
        target1 = CallbackOutputActionTarget()
        target1.initialize({'callback': callback1})
        
        target2 = CallbackOutputActionTarget()
        target2.initialize({'callback': callback2})
        
        # Add targets
        dispatcher.add_target(target1)
        dispatcher.add_target(target2)
        
        # Dispatch text
        test_metadata = {'confidence': 0.95, 'test': True}
        assert dispatcher.dispatch_text("hello world", test_metadata) == True
        
        # Check both targets received text
        assert len(calls1) == 1
        assert len(calls2) == 1
        assert calls1[0][0] == "hello world"
        assert calls2[0][0] == "hello world"
        
        # Check metadata was passed and timestamp added
        assert calls1[0][1]['confidence'] == 0.95
        assert calls1[0][1]['test'] == True
        assert 'timestamp' in calls1[0][1]
        
        print("OutputDispatcher text dispatch works correctly")
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_output_dispatcher_event_listeners():
    """Test event listener functionality."""
    try:
        from voice_typing.interfaces.output_action import OutputDispatcher
        
        dispatcher = OutputDispatcher()
        dispatcher.initialize()
        
        # Add event listeners
        listener_calls = []
        def event_listener(text, metadata):
            listener_calls.append((text, metadata))
        
        dispatcher.add_event_listener(event_listener)
        
        # Dispatch text
        dispatcher.dispatch_text("test message", {'test': True})
        
        # Check listener was called
        assert len(listener_calls) == 1
        assert listener_calls[0][0] == "test message"
        assert listener_calls[0][1]['test'] == True
        
        # Test removing listener
        assert dispatcher.remove_event_listener(event_listener) == True
        assert dispatcher.remove_event_listener(event_listener) == False  # Already removed
        
        # Dispatch again - listener should not be called
        listener_calls.clear()
        dispatcher.dispatch_text("another message")
        assert len(listener_calls) == 0
        
        print("OutputDispatcher event listeners work correctly")
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_output_dispatcher_error_handling():
    """Test error handling in OutputDispatcher."""
    try:
        from voice_typing.interfaces.output_action import (
            OutputDispatcher,
            CallbackOutputActionTarget
        )
        
        dispatcher = OutputDispatcher()
        dispatcher.initialize()
        
        # Create target that raises exception
        def failing_callback(text, metadata):
            raise Exception("Test exception")
        
        failing_target = CallbackOutputActionTarget()
        failing_target.initialize({'callback': failing_callback})
        dispatcher.add_target(failing_target)
        
        # Create working target
        working_calls = []
        def working_callback(text, metadata):
            working_calls.append((text, metadata))
        
        working_target = CallbackOutputActionTarget()
        working_target.initialize({'callback': working_callback})
        dispatcher.add_target(working_target)
        
        # Dispatch text - should not crash despite failing target
        result = dispatcher.dispatch_text("test")
        
        # Working target should still receive text
        assert len(working_calls) == 1
        assert working_calls[0][0] == "test"
        
        print("OutputDispatcher error handling works correctly")
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_keyboard_output_target():
    """Test KeyboardOutputActionTarget functionality."""
    try:
        from voice_typing.interfaces.output_action import (
            KeyboardOutputActionTarget,
            OutputType
        )
        
        keyboard_target = KeyboardOutputActionTarget()
        
        # Test output type
        assert keyboard_target.get_output_type() == OutputType.KEYBOARD
        assert keyboard_target.supports_formatting() == False
        
        # Test initialization
        config = {'append_space': False}
        # Note: This might fail if xdotool is not available, which is expected
        keyboard_target.initialize(config)
        
        print("KeyboardOutputActionTarget basic functionality works")
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_output_dispatcher_cleanup():
    """Test OutputDispatcher cleanup functionality."""
    try:
        from voice_typing.interfaces.output_action import (
            OutputDispatcher,
            CallbackOutputActionTarget
        )
        
        dispatcher = OutputDispatcher()
        dispatcher.initialize()
        
        # Add target and listener
        target = CallbackOutputActionTarget()
        target.initialize({'callback': lambda text, meta: None})
        dispatcher.add_target(target)
        
        listener = lambda text, meta: None
        dispatcher.add_event_listener(listener)
        
        assert dispatcher.get_target_count() == 1
        
        # Test cleanup
        dispatcher.cleanup()
        assert not dispatcher.is_initialized()
        assert dispatcher.get_target_count() == 0
        
        print("OutputDispatcher cleanup works correctly")
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_output_dispatcher_empty_text_handling():
    """Test handling of empty or None text."""
    try:
        from voice_typing.interfaces.output_action import (
            OutputDispatcher,
            CallbackOutputActionTarget
        )
        
        dispatcher = OutputDispatcher()
        dispatcher.initialize()
        
        # Add target
        calls = []
        target = CallbackOutputActionTarget()
        target.initialize({'callback': lambda text, meta: calls.append((text, meta))})
        dispatcher.add_target(target)
        
        # Test empty text
        result = dispatcher.dispatch_text("")
        assert result == False
        assert len(calls) == 0
        
        # Test None text (should be handled gracefully)
        result = dispatcher.dispatch_text(None)
        assert result == False
        assert len(calls) == 0
        
        print("OutputDispatcher empty text handling works correctly")
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")

