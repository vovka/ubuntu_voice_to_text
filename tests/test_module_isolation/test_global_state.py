"""
Unit tests for GlobalState class.

Tests the global state management functionality in isolation.
"""

import pytest
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def test_global_state_initialization():
    """Test GlobalState initialization with default values."""
    from voice_typing.global_state import GlobalState
    
    state = GlobalState()
    
    # Verify default values
    assert state.state == "idle"
    assert state.icon is None
    assert state.current_keys == set()
    assert hasattr(state, 'q')  # Queue should exist
    assert state.q.empty()  # Queue should be empty


def test_global_state_state_property():
    """Test state property can be read and written."""
    from voice_typing.global_state import GlobalState
    
    state = GlobalState()
    
    # Test initial state
    assert state.state == "idle"
    
    # Test state changes
    state.state = "listening"
    assert state.state == "listening"
    
    state.state = "finish_listening"
    assert state.state == "finish_listening"
    
    state.state = "idle"
    assert state.state == "idle"


def test_global_state_current_keys_property():
    """Test current_keys property can be modified."""
    from voice_typing.global_state import GlobalState
    
    state = GlobalState()
    
    # Test initial empty set
    assert state.current_keys == set()
    
    # Test adding keys
    state.current_keys.add("ctrl")
    assert "ctrl" in state.current_keys
    
    state.current_keys.add("shift")
    assert "ctrl" in state.current_keys
    assert "shift" in state.current_keys
    
    # Test removing keys
    state.current_keys.remove("ctrl")
    assert "ctrl" not in state.current_keys
    assert "shift" in state.current_keys
    
    # Test clearing keys
    state.current_keys.clear()
    assert state.current_keys == set()


def test_global_state_queue_functionality():
    """Test queue functionality."""
    from voice_typing.global_state import GlobalState
    
    state = GlobalState()
    
    # Test queue is initially empty
    assert state.q.empty()
    
    # Test putting items in queue
    state.q.put("test_item_1")
    assert not state.q.empty()
    assert state.q.qsize() == 1
    
    state.q.put("test_item_2")
    assert state.q.qsize() == 2
    
    # Test getting items from queue (FIFO)
    item1 = state.q.get()
    assert item1 == "test_item_1"
    assert state.q.qsize() == 1
    
    item2 = state.q.get()
    assert item2 == "test_item_2"
    assert state.q.empty()


def test_global_state_icon_property():
    """Test icon property can be set and retrieved."""
    from voice_typing.global_state import GlobalState
    
    state = GlobalState()
    
    # Test initial None value
    assert state.icon is None
    
    # Test setting icon
    mock_icon = "mock_icon_object"
    state.icon = mock_icon
    assert state.icon == mock_icon
    
    # Test setting to None
    state.icon = None
    assert state.icon is None


def test_global_state_multiple_instances():
    """Test that GlobalState instances initially share class variables."""
    from voice_typing.global_state import GlobalState
    
    # Create two instances
    state1 = GlobalState()
    state2 = GlobalState()
    
    # Initially they share the same class variables
    assert state1.q is state2.q  # Queue is shared
    assert state1.current_keys is state2.current_keys  # Set is shared
    assert state1.icon is state2.icon  # Icon is shared
    
    # State starts the same but becomes instance-specific when modified
    assert state1.state == state2.state == "idle"  # Initially same
    
    # Modifying state becomes instance-specific
    state1.state = "listening"
    assert state1.state == "listening"
    assert state2.state == "idle"  # state2 retains original value
    
    # But shared objects are still shared
    state1.current_keys.add("test_key")
    assert "test_key" in state2.current_keys
    
    state1.q.put("shared_item")
    assert not state2.q.empty()
    item = state2.q.get()
    assert item == "shared_item"


def test_global_state_valid_states():
    """Test setting various valid state values."""
    from voice_typing.global_state import GlobalState
    
    state = GlobalState()
    
    # Test all documented valid states
    valid_states = ["idle", "listening", "finish_listening"]
    
    for valid_state in valid_states:
        state.state = valid_state
        assert state.state == valid_state
    
    # Test custom states (should also work since it's just a string property)
    state.state = "custom_state"
    assert state.state == "custom_state"


def test_global_state_key_combinations():
    """Test storing various key combinations."""
    from voice_typing.global_state import GlobalState
    
    state = GlobalState()
    
    # Test common key combinations
    state.current_keys = {"ctrl", "shift", "a"}
    assert len(state.current_keys) == 3
    assert "ctrl" in state.current_keys
    assert "shift" in state.current_keys
    assert "a" in state.current_keys
    
    # Test replacing key combination
    state.current_keys = {"alt", "tab"}
    assert len(state.current_keys) == 2
    assert "alt" in state.current_keys
    assert "tab" in state.current_keys
    assert "ctrl" not in state.current_keys  # Previous keys should be gone


if __name__ == "__main__":
    # Run tests manually if called directly
    test_global_state_initialization()
    test_global_state_state_property()
    test_global_state_current_keys_property()
    test_global_state_queue_functionality()
    test_global_state_icon_property()
    test_global_state_multiple_instances()
    test_global_state_valid_states()
    test_global_state_key_combinations()
    
    print("✅ All GlobalState unit tests passed!")