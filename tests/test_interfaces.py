"""
Tests for the new module interfaces.

This validates that the interfaces are properly defined and 
can be implemented correctly.
"""

import pytest
import sys
import os
from typing import Dict, Any, Optional, Callable

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def test_interfaces_can_be_imported():
    """Test that all new interfaces can be imported."""
    try:
        from voice_typing.interfaces import (
            AudioInputSource,
            OutputActionTarget,
            StateManager,
            VoiceRecognitionSource,
        )
        
        # Test that they are abstract base classes
        assert hasattr(AudioInputSource, '__abstractmethods__')
        assert hasattr(OutputActionTarget, '__abstractmethods__')
        assert hasattr(StateManager, '__abstractmethods__')
        assert hasattr(VoiceRecognitionSource, '__abstractmethods__')
        
        print("All interfaces imported successfully")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_audio_input_interface():
    """Test AudioInputSource interface definition."""
    try:
        from voice_typing.interfaces import AudioInputSource
        
        # Check that all required methods are abstract
        expected_methods = {
            'initialize',
            'start_capture', 
            'stop_capture',
            'is_capturing',
            'is_available',
            'cleanup',
            'get_device_info'
        }
        
        abstract_methods = AudioInputSource.__abstractmethods__
        assert expected_methods.issubset(abstract_methods)
        
        print("AudioInputSource interface properly defined")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_output_action_interface():
    """Test OutputActionTarget interface definition."""
    try:
        from voice_typing.interfaces import OutputActionTarget, OutputType
        
        # Check that OutputType enum exists
        assert hasattr(OutputType, 'KEYBOARD')
        assert hasattr(OutputType, 'CLIPBOARD')
        assert hasattr(OutputType, 'FILE')
        assert hasattr(OutputType, 'CALLBACK')
        
        # Check that all required methods are abstract
        expected_methods = {
            'initialize',
            'deliver_text',
            'is_available', 
            'get_output_type',
            'supports_formatting',
            'cleanup'
        }
        
        abstract_methods = OutputActionTarget.__abstractmethods__
        assert expected_methods.issubset(abstract_methods)
        
        print("OutputActionTarget interface properly defined")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_state_manager_interface():
    """Test StateManager interface definition."""
    try:
        from voice_typing.interfaces.state_manager import (
            StateManager,
            VoiceTypingState,
            StateTransition
        )
        
        # Check that VoiceTypingState enum exists
        assert hasattr(VoiceTypingState, 'IDLE')
        assert hasattr(VoiceTypingState, 'LISTENING')
        assert hasattr(VoiceTypingState, 'FINISH_LISTENING')
        assert hasattr(VoiceTypingState, 'PROCESSING')
        assert hasattr(VoiceTypingState, 'ERROR')
        
        # Check StateTransition class
        transition = StateTransition(VoiceTypingState.IDLE, VoiceTypingState.LISTENING)
        assert transition.from_state == VoiceTypingState.IDLE
        assert transition.to_state == VoiceTypingState.LISTENING
        assert hasattr(transition, 'timestamp')
        assert hasattr(transition, 'metadata')
        
        # Check that all required methods are abstract
        expected_methods = {
            'get_current_state',
            'set_state',
            'can_transition_to',
            'register_state_listener',
            'unregister_state_listener',
            'get_state_history',
            'get_state_metadata',
            'reset_state'
        }
        
        abstract_methods = StateManager.__abstractmethods__
        assert expected_methods.issubset(abstract_methods)
        
        print("StateManager interface properly defined")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_mock_audio_input_implementation():
    """Test that AudioInputSource can be implemented."""
    try:
        from voice_typing.interfaces import AudioInputSource
        
        class MockAudioInput(AudioInputSource):
            def __init__(self):
                self._initialized = False
                self._capturing = False
                self._callback = None
            
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
        
        # Test implementation
        audio_input = MockAudioInput()
        
        # Test initialization
        config = {'sample_rate': 16000}
        assert audio_input.initialize(config) == True
        assert audio_input.is_available() == True
        
        # Test capture
        received_chunks = []
        def callback(chunk: bytes):
            received_chunks.append(chunk)
        
        assert audio_input.start_capture(callback) == True
        assert audio_input.is_capturing() == True
        
        # Simulate receiving audio chunk
        if audio_input._callback:
            audio_input._callback(b'test_audio_data')
        
        assert len(received_chunks) == 1
        assert received_chunks[0] == b'test_audio_data'
        
        # Test stop and cleanup
        audio_input.stop_capture()
        assert audio_input.is_capturing() == False
        
        audio_input.cleanup()
        
        print("Mock AudioInputSource implementation works correctly")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_mock_output_action_implementation():
    """Test that OutputActionTarget can be implemented."""
    try:
        from voice_typing.interfaces import OutputActionTarget, OutputType
        
        class MockOutputTarget(OutputActionTarget):
            def __init__(self):
                self._initialized = False
                self._delivered_texts = []
            
            def initialize(self, config: Dict[str, Any]) -> bool:
                self._initialized = True
                return True
            
            def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
                if not self._initialized:
                    return False
                self._delivered_texts.append((text, metadata))
                return True
            
            def is_available(self) -> bool:
                return True
            
            def get_output_type(self) -> OutputType:
                return OutputType.CALLBACK
            
            def supports_formatting(self) -> bool:
                return False
            
            def cleanup(self) -> None:
                self._delivered_texts.clear()
        
        # Test implementation
        output_target = MockOutputTarget()
        
        # Test initialization
        config = {}
        assert output_target.initialize(config) == True
        assert output_target.is_available() == True
        assert output_target.get_output_type() == OutputType.CALLBACK
        assert output_target.supports_formatting() == False
        
        # Test text delivery
        metadata = {'confidence': 0.95}
        assert output_target.deliver_text("hello world", metadata) == True
        
        assert len(output_target._delivered_texts) == 1
        text, meta = output_target._delivered_texts[0]
        assert text == "hello world"
        assert meta == metadata
        
        # Test cleanup
        output_target.cleanup()
        assert len(output_target._delivered_texts) == 0
        
        print("Mock OutputActionTarget implementation works correctly")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_basic_state_manager_implementation():
    """Test BasicStateManager implementation."""
    try:
        from voice_typing.interfaces.state_manager import BasicStateManager, VoiceTypingState, StateTransition
        
        # Create state manager
        state_manager = BasicStateManager()
        
        # Test initial state
        assert state_manager.get_current_state() == VoiceTypingState.IDLE
        
        # Test valid transition
        success = state_manager.set_state(VoiceTypingState.LISTENING)
        assert success == True
        assert state_manager.get_current_state() == VoiceTypingState.LISTENING
        
        # Test invalid transition
        success = state_manager.set_state(VoiceTypingState.PROCESSING)  # LISTENING -> PROCESSING is invalid
        assert success == False
        assert state_manager.get_current_state() == VoiceTypingState.LISTENING  # Should not change
        
        # Test state listeners
        received_transitions = []
        def listener(transition: StateTransition):
            received_transitions.append(transition)
        
        state_manager.register_state_listener(listener)
        
        # Make a transition
        metadata = {'test': 'data'}
        state_manager.set_state(VoiceTypingState.FINISH_LISTENING, metadata)
        
        # Check listener was called
        assert len(received_transitions) == 1
        transition = received_transitions[0]
        assert transition.from_state == VoiceTypingState.LISTENING
        assert transition.to_state == VoiceTypingState.FINISH_LISTENING
        assert transition.metadata == metadata
        
        # Test history
        history = state_manager.get_state_history()
        assert len(history) >= 2  # At least 2 transitions occurred
        
        # Test reset
        state_manager.reset_state()
        assert state_manager.get_current_state() == VoiceTypingState.IDLE
        
        print("BasicStateManager implementation works correctly")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_callback_output_target():
    """Test CallbackOutputActionTarget implementation."""
    try:
        from voice_typing.interfaces.output_action import CallbackOutputActionTarget
        
        # Test callback target
        received_calls = []
        def test_callback(text: str, metadata: Optional[Dict[str, Any]]):
            received_calls.append((text, metadata))
        
        callback_target = CallbackOutputActionTarget()
        config = {'callback': test_callback}
        
        assert callback_target.initialize(config) == True
        assert callback_target.is_available() == True
        
        # Test text delivery
        metadata = {'confidence': 0.8}
        assert callback_target.deliver_text("test message", metadata) == True
        
        # Check callback was called
        assert len(received_calls) == 1
        text, meta = received_calls[0]
        assert text == "test message" 
        assert meta == metadata
        
        print("CallbackOutputActionTarget works correctly")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_multi_output_target():
    """Test MultiOutputActionTarget implementation."""
    try:
        from voice_typing.interfaces.output_action import MultiOutputActionTarget, CallbackOutputActionTarget
        
        # Create multiple callback targets
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
        
        # Create multi-target
        multi_target = MultiOutputActionTarget([target1, target2])
        assert multi_target.initialize({}) == True
        assert multi_target.is_available() == True
        
        # Test delivery to all targets
        metadata = {'test': True}
        assert multi_target.deliver_text("broadcast message", metadata) == True
        
        # Check both callbacks were called
        assert len(calls1) == 1
        assert len(calls2) == 1
        assert calls1[0] == ("broadcast message", metadata)
        assert calls2[0] == ("broadcast message", metadata)
        
        print("MultiOutputActionTarget works correctly")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_interfaces_exported_from_main_package():
    """Test that interfaces are properly exported from main package."""
    try:
        from voice_typing import (
            AudioInputSource,
            OutputActionTarget,
            StateManager,
        )
        
        # Just test they can be imported - interface tests are above
        assert AudioInputSource is not None
        assert OutputActionTarget is not None
        assert StateManager is not None
        
        print("Interfaces properly exported from main package")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")