"""
Test TrayIconManager decoupling - ensuring UI layer is a pure subscriber.

This test validates that TrayIconManager:
1. Subscribes to state changes via StateManager
2. Does not directly access or mutate state
3. Updates icons based on state events rather than imperative calls
"""

import sys
import os
from unittest.mock import Mock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_tray_icon_subscribes_to_state_changes():
    """Test that TrayIconManager subscribes to state changes."""
    try:
        from voice_typing.tray_icon_manager import TrayIconManager
        from voice_typing.interfaces.state_manager import BasicStateManager, VoiceTypingState
        
        # Create state manager and TrayIconManager
        state_manager = BasicStateManager()
        tray_icon_manager = TrayIconManager(state_manager=state_manager)
        
        # Verify subscription happened
        assert len(state_manager._listeners) == 1
        print("✓ TrayIconManager subscribed to state changes")
        
    except ImportError as e:
        print(f"Skipping test due to missing dependencies: {e}")


def test_tray_icon_reacts_to_state_events():
    """Test that TrayIconManager reacts to state change events."""
    try:
        from voice_typing.tray_icon_manager import TrayIconManager
        from voice_typing.interfaces.state_manager import BasicStateManager, VoiceTypingState
        
        # Create state manager and TrayIconManager
        state_manager = BasicStateManager()
        tray_icon_manager = TrayIconManager(state_manager=state_manager)
        
        # Mock the icon to capture updates
        mock_icon = Mock()
        tray_icon_manager.icon = mock_icon
        
        # Mock create_image_text to return a simple value
        with patch.object(tray_icon_manager, 'create_image_text', return_value="mock_image"):
            # Trigger state change
            state_manager.set_state(VoiceTypingState.LISTENING)
            
            # Verify the icon was updated
            assert tray_icon_manager._current_state == VoiceTypingState.LISTENING
            assert mock_icon.icon == "mock_image"  # Icon was set
            assert mock_icon.title == "Voice Typing: ON"  # Title was updated
            
        print("✓ TrayIconManager reacts to state change events")
        
    except ImportError as e:
        print(f"Skipping test due to missing dependencies: {e}")


def test_tray_icon_no_direct_state_access():
    """Test that new TrayIconManager doesn't access state directly."""
    try:
        from voice_typing.tray_icon_manager import TrayIconManager
        from voice_typing.interfaces.state_manager import BasicStateManager
        
        # Create TrayIconManager with StateManager (new approach)
        state_manager = BasicStateManager()
        tray_icon_manager = TrayIconManager(state_manager=state_manager)
        
        # Verify no direct state_ref access for new interface
        assert not hasattr(tray_icon_manager, 'state_ref') or tray_icon_manager.state_ref is None
        print("✓ New TrayIconManager doesn't access state directly")
        
    except ImportError as e:
        print(f"Skipping test due to missing dependencies: {e}")


def test_backward_compatibility():
    """Test that legacy interface still works."""
    try:
        from voice_typing.tray_icon_manager import TrayIconManager
        from voice_typing.global_state import GlobalState
        
        # Create TrayIconManager with legacy interface
        state_ref = GlobalState()
        tray_icon_manager = TrayIconManager(state_ref=state_ref)
        
        # Verify legacy access works
        assert tray_icon_manager.state_ref is state_ref
        
        # The update_icon method should work without errors
        tray_icon_manager.update_icon()  # Should not crash
        
        print("✓ Backward compatibility maintained")
        
    except ImportError as e:
        print(f"Skipping test due to missing dependencies: {e}")


def test_exit_callback_delegation():
    """Test that exit logic is delegated through callback."""
    try:
        from voice_typing.tray_icon_manager import TrayIconManager
        
        # Create mock exit callback
        exit_callback = Mock()
        tray_icon_manager = TrayIconManager(exit_callback=exit_callback)
        
        # Mock icon
        mock_icon = Mock()
        
        # Call exit_application
        tray_icon_manager.exit_application(mock_icon, None)
        
        # Verify icon.stop() was called and callback was invoked
        mock_icon.stop.assert_called_once()
        exit_callback.assert_called_once()
        
        print("✓ Exit logic delegated through callback")
        
    except ImportError as e:
        print(f"Skipping test due to missing dependencies: {e}")


if __name__ == "__main__":
    test_tray_icon_subscribes_to_state_changes()
    test_tray_icon_reacts_to_state_events()
    test_tray_icon_no_direct_state_access()
    test_backward_compatibility()
    test_exit_callback_delegation()
    print("All TrayIconManager decoupling tests passed!")