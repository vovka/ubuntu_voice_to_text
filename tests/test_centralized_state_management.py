"""
Tests for centralized state management integration.

This test validates that the state management is properly centralized 
and that state transitions are logged and testable.
"""

import pytest
import sys  
import os

def test_state_manager_integration():
    """Test that StateManager is properly integrated into the main application."""
    # Add the project root to the path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    try:
        from voice_typing.interfaces.state_manager import (
            LegacyStateManagerAdapter, 
            VoiceTypingState,
            StateTransition
        )
        from voice_typing import GlobalState
        
        # Test integration works
        state_ref = GlobalState()
        state_manager = LegacyStateManagerAdapter(state_ref)
        
        # Test that state manager wraps the global state properly
        assert state_manager.get_current_state() == VoiceTypingState.IDLE
        assert state_ref.state == "idle"
        
        # Test state transitions are logged and tracked
        transitions = []
        def capture_transitions(transition: StateTransition):
            transitions.append(transition)
        
        state_manager.register_state_listener(capture_transitions)
        
        # Make a state transition
        success = state_manager.set_state(VoiceTypingState.LISTENING, 
                                        metadata={'test': 'integration'})
        assert success
        assert state_manager.get_current_state() == VoiceTypingState.LISTENING
        assert state_ref.state == "listening"
        
        # Verify transition was logged
        assert len(transitions) == 1
        transition = transitions[0]
        assert transition.from_state == VoiceTypingState.IDLE
        assert transition.to_state == VoiceTypingState.LISTENING
        assert transition.metadata == {'test': 'integration'}
        
        # Test history tracking
        history = state_manager.get_state_history()
        assert len(history) == 1
        assert history[0].from_state == VoiceTypingState.IDLE
        assert history[0].to_state == VoiceTypingState.LISTENING
        
        print("✅ StateManager integration test passed")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_hotkey_manager_state_manager_integration():
    """Test that HotkeyManager uses StateManager for state transitions."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    try:
        from voice_typing.interfaces.state_manager import (
            LegacyStateManagerAdapter,
            VoiceTypingState
        )
        from voice_typing import GlobalState, Config, HotkeyManager
        
        # Set up components
        config = Config()
        state_ref = GlobalState()
        state_manager = LegacyStateManagerAdapter(state_ref)
        
        # Track state transitions
        transitions = []
        def capture_transitions(transition):
            transitions.append(transition)
        state_manager.register_state_listener(capture_transitions)
        
        # Create hotkey manager with state manager
        hotkey_manager = HotkeyManager(
            config, state_ref, None, None, state_manager
        )
        
        # Test that hotkey manager uses state manager
        hotkey_manager.set_state("listening")
        
        # Verify transition was managed by StateManager
        assert len(transitions) == 1
        assert transitions[0].from_state == VoiceTypingState.IDLE
        assert transitions[0].to_state == VoiceTypingState.LISTENING
        assert transitions[0].metadata == {'source': 'hotkey_manager'}
        
        # Verify state was actually changed
        assert state_manager.get_current_state() == VoiceTypingState.LISTENING
        assert state_ref.state == "listening"
        
        print("✅ HotkeyManager StateManager integration test passed")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_backward_compatibility():
    """Test that components still work without StateManager (backward compatibility)."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    try:
        from voice_typing import GlobalState, Config, HotkeyManager
        
        # Set up components WITHOUT state manager
        config = Config()
        state_ref = GlobalState()
        
        # Create hotkey manager without state manager (backward compatibility)
        hotkey_manager = HotkeyManager(
            config, state_ref, None, None, None  # state_manager=None
        )
        
        # Test that it still works with direct state mutation
        hotkey_manager.set_state("listening")
        assert state_ref.state == "listening"
        
        hotkey_manager.set_state("idle")
        assert state_ref.state == "idle"
        
        print("✅ Backward compatibility test passed")
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")