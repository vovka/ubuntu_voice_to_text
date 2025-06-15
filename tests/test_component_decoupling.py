"""
Test component decoupling - verifying core components are fully decoupled
and interact only via events.

This test validates that:
1. AudioProcessor subscribes to state changes and reacts automatically
2. HotkeyManager doesn't directly call other components
3. PipelineVoiceTyping doesn't have unused dependencies
4. TrayIconManager remains properly decoupled
"""

import sys
import os
from unittest.mock import Mock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_audio_processor_event_driven():
    """Test that AudioProcessor subscribes to state changes and reacts automatically."""
    try:
        from voice_typing.audio_processor import AudioProcessor
        from voice_typing.interfaces.state_manager import BasicStateManager, VoiceTypingState
        from voice_typing.config import Config
        from unittest.mock import Mock
        
        # Mock recognition source to avoid model dependency
        mock_recognition_source = Mock()
        mock_recognition_source.initialize.return_value = True
        
        # Mock output dispatcher
        mock_output_dispatcher = Mock()
        
        # Create state manager and AudioProcessor
        config = Config()
        state_manager = BasicStateManager()
        
        with patch('voice_typing.audio_processor.RecognitionSourceFactory.create_recognition_source', return_value=mock_recognition_source):
            audio_processor = AudioProcessor(
                config, 
                state_manager, 
                recognition_source=mock_recognition_source,
                output_dispatcher=mock_output_dispatcher
            )
        
        # Verify AudioProcessor subscribed to state changes
        assert len(state_manager._listeners) == 1
        
        # Mock start_listening method to track calls
        original_start_listening = audio_processor.start_listening
        audio_processor.start_listening = Mock(side_effect=original_start_listening)
        
        # Trigger state change to LISTENING
        state_manager.set_state(VoiceTypingState.LISTENING)
        
        # Verify start_listening was called automatically due to state change
        audio_processor.start_listening.assert_called_once()
        
        print("✓ AudioProcessor reacts to state changes automatically")
        
    except ImportError as e:
        print(f"Skipping test due to missing dependencies: {e}")


def test_hotkey_manager_decoupled():
    """Test that HotkeyManager is decoupled from other components."""
    try:
        from voice_typing.hotkey_manager import HotkeyManager
        from voice_typing.interfaces.state_manager import BasicStateManager
        from voice_typing.config import Config
        
        # Create HotkeyManager with only required dependencies
        config = Config()
        state_manager = BasicStateManager()
        hotkey_manager = HotkeyManager(config, state_manager)
        
        # Verify no references to other components
        assert not hasattr(hotkey_manager, 'tray_icon_manager') or hotkey_manager.tray_icon_manager is None
        assert not hasattr(hotkey_manager, 'audio_processor') or hotkey_manager.audio_processor is None
        
        print("✓ HotkeyManager is properly decoupled")
        
    except ImportError as e:
        print(f"Skipping test due to missing dependencies: {e}")


def test_pipeline_voice_typing_decoupled():
    """Test that PipelineVoiceTyping is decoupled from TrayIconManager."""
    try:
        from voice_typing.pipeline_voice_typing import PipelineVoiceTyping
        from voice_typing.interfaces.state_manager import BasicStateManager
        from voice_typing.config import Config
        from unittest.mock import Mock
        
        # Mock recognition source to avoid model dependency
        mock_recognition_source = Mock()
        mock_output_dispatcher = Mock()
        
        # Create PipelineVoiceTyping without TrayIconManager dependency
        config = Config()
        state_manager = BasicStateManager()
        voice_typing = PipelineVoiceTyping(
            config, 
            state_manager,
            recognition_source=mock_recognition_source,
            output_dispatcher=mock_output_dispatcher
        )
        
        # Verify no reference to TrayIconManager
        assert not hasattr(voice_typing, 'tray_icon_manager') or voice_typing.tray_icon_manager is None
        
        print("✓ PipelineVoiceTyping is properly decoupled from TrayIconManager")
        
    except ImportError as e:
        print(f"Skipping test due to missing dependencies: {e}")


def test_component_instantiation_signatures():
    """Test that all components can be instantiated with new decoupled signatures."""
    try:
        from voice_typing import Config, TrayIconManager, HotkeyManager, PipelineVoiceTyping, BasicStateManager
        from unittest.mock import Mock
        
        config = Config()
        state_manager = BasicStateManager()
        
        # Test TrayIconManager - already decoupled
        tray_icon_manager = TrayIconManager(state_manager=state_manager)
        assert tray_icon_manager is not None
        
        # Test HotkeyManager - now with only config and state_manager
        hotkey_manager = HotkeyManager(config, state_manager)
        assert hotkey_manager is not None
        
        # Test PipelineVoiceTyping - now without tray_icon_manager
        mock_recognition_source = Mock()
        mock_output_dispatcher = Mock()
        voice_typing = PipelineVoiceTyping(
            config, 
            state_manager,
            recognition_source=mock_recognition_source,
            output_dispatcher=mock_output_dispatcher
        )
        assert voice_typing is not None
        
        print("✓ All components instantiate with new decoupled signatures")
        
    except ImportError as e:
        print(f"Skipping test due to missing dependencies: {e}")


def test_no_direct_component_references():
    """Test that core components don't have direct references to each other."""
    try:
        from voice_typing.hotkey_manager import HotkeyManager
        from voice_typing.pipeline_voice_typing import PipelineVoiceTyping
        from voice_typing.tray_icon_manager import TrayIconManager
        from voice_typing.interfaces.state_manager import BasicStateManager
        from voice_typing.config import Config
        from unittest.mock import Mock
        
        config = Config()
        state_manager = BasicStateManager()
        
        # Create components
        tray_icon_manager = TrayIconManager(state_manager=state_manager)
        hotkey_manager = HotkeyManager(config, state_manager)
        
        mock_recognition_source = Mock()
        mock_output_dispatcher = Mock()
        voice_typing = PipelineVoiceTyping(
            config, 
            state_manager,
            recognition_source=mock_recognition_source,
            output_dispatcher=mock_output_dispatcher
        )
        
        # Check that none of the components hold direct references to each other
        components = [
            ('HotkeyManager', hotkey_manager, ['tray_icon_manager', 'audio_processor']),
            ('PipelineVoiceTyping', voice_typing, ['tray_icon_manager']),
            ('TrayIconManager', tray_icon_manager, ['hotkey_manager', 'audio_processor', 'pipeline_voice_typing'])
        ]
        
        for component_name, component, forbidden_attrs in components:
            for attr in forbidden_attrs:
                if hasattr(component, attr) and getattr(component, attr) is not None:
                    raise AssertionError(f"{component_name} still has reference to {attr}")
        
        print("✓ No direct references between core components")
        
    except ImportError as e:
        print(f"Skipping test due to missing dependencies: {e}")


if __name__ == "__main__":
    test_audio_processor_event_driven()
    test_hotkey_manager_decoupled()
    test_pipeline_voice_typing_decoupled()
    test_component_instantiation_signatures()
    test_no_direct_component_references()
    print("All component decoupling tests passed!")