"""
Unit tests for LinuxKeyboardListener implementation.

These tests verify the functionality of the LinuxKeyboardListener
and ensure it properly integrates with the interface contract.
"""

import asyncio
import pytest
import logging
from unittest.mock import Mock, patch, MagicMock

from interfaces.keyboard_listener import IKeyboardListener
from voice_typing.keyboard_listener.linux_keyboard_listener import LinuxKeyboardListener, Key, KeyCode


class TestLinuxKeyboardListener:
    """Test suite for LinuxKeyboardListener implementation."""

    def test_linux_keyboard_listener_implements_interface(self):
        """Test that LinuxKeyboardListener implements IKeyboardListener."""
        listener = LinuxKeyboardListener()
        assert isinstance(listener, IKeyboardListener)
        assert hasattr(listener, "output_queue")
        assert hasattr(listener, "run")
        assert hasattr(listener, "stop")

    def test_linux_keyboard_listener_initialization(self):
        """Test proper initialization of LinuxKeyboardListener."""
        config = {"hotkeys": ["ctrl+shift+alt+a"]}
        output_queue = asyncio.Queue()
        
        listener = LinuxKeyboardListener(config=config, output_queue=output_queue)
        
        assert listener._config == config
        assert listener.output_queue is output_queue
        assert listener._running is False
        assert listener._listener is None

    def test_linux_keyboard_listener_default_queue(self):
        """Test that LinuxKeyboardListener creates default queue if none provided."""
        listener = LinuxKeyboardListener()
        assert listener.output_queue is not None
        assert hasattr(listener.output_queue, "put")
        assert hasattr(listener.output_queue, "get")

    @pytest.mark.asyncio
    async def test_linux_keyboard_listener_queue_interaction(self):
        """Test that LinuxKeyboardListener can interact with output queue."""
        listener = LinuxKeyboardListener()
        
        # Test putting event to queue
        test_event = "test_hotkey_event"
        await listener.output_queue.put(test_event)
        
        # Test getting event from queue
        retrieved_event = await listener.output_queue.get()
        assert retrieved_event == test_event

    def test_is_target_hotkey_pressed_logic(self):
        """Test the hotkey detection logic."""
        listener = LinuxKeyboardListener()
        
        # Test left-side modifiers + 'a'
        listener._current_keys = {Key.ctrl_l, Key.shift_l, Key.alt_l, KeyCode.from_char('a')}
        assert listener._is_target_hotkey_pressed() is True
        
        # Test right-side modifiers + 'a'
        listener._current_keys = {Key.ctrl_r, Key.shift_r, Key.alt_r, KeyCode.from_char('a')}
        assert listener._is_target_hotkey_pressed() is True
        
        # Test mixed modifiers + 'a'
        listener._current_keys = {Key.ctrl_l, Key.shift_l, Key.alt_r, KeyCode.from_char('a')}
        assert listener._is_target_hotkey_pressed() is True
        
        # Test incomplete combination
        listener._current_keys = {Key.ctrl_l, Key.shift_l}
        assert listener._is_target_hotkey_pressed() is False
        
        # Test wrong key
        listener._current_keys = {Key.ctrl_l, Key.shift_l, Key.alt_l, KeyCode.from_char('b')}
        assert listener._is_target_hotkey_pressed() is False

    @pytest.mark.asyncio
    async def test_linux_keyboard_listener_fallback_mode(self):
        """Test the fallback mode when pynput is not available."""
        listener = LinuxKeyboardListener()
        
        # Since pynput is not available in this environment, test fallback mode
        task = asyncio.create_task(listener.run())
        
        # Give it a moment to start and potentially send fallback event
        await asyncio.sleep(0.1)
        
        # Stop the listener
        listener.stop()
        
        # Cancel the task
        task.cancel()
        
        # Wait for the task to complete
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_send_hotkey_event(self):
        """Test the _send_hotkey_event method."""
        listener = LinuxKeyboardListener()
        
        # Send a hotkey event (first call should be start_recording)
        await listener._send_hotkey_event()
        
        # Verify the event was put in the queue
        event = await listener.output_queue.get()
        assert event == "ctrl+shift+start_recording"
        
        # Send another hotkey event (should toggle to stop_recording)
        await listener._send_hotkey_event()
        
        # Verify the second event
        event = await listener.output_queue.get()
        assert event == "ctrl+shift+stop_recording"

    def test_on_press_on_release_handlers(self):
        """Test the key press and release handlers."""
        listener = LinuxKeyboardListener()
        
        # Test key press
        listener._on_press(Key.ctrl_l)
        assert Key.ctrl_l in listener._current_keys
        
        # Test key release
        listener._on_release(Key.ctrl_l)
        assert Key.ctrl_l not in listener._current_keys

    def test_stop_method(self):
        """Test the stop method."""
        listener = LinuxKeyboardListener()
        
        # Test stop method
        listener.stop()
        assert listener._running is False


if __name__ == "__main__":
    pytest.main([__file__])