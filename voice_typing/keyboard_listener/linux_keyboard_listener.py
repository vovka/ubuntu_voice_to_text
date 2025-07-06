"""
Linux keyboard listener implementation using pynput for global hotkey detection.

This implementation provides real keyboard listening functionality for Ubuntu
using the pynput library to capture global hotkey combinations.
"""

import asyncio
import logging
import threading
from typing import Any, Dict, Optional

from interfaces.keyboard_listener import IKeyboardListener
from interfaces.queue_protocol import QueueProtocol

# Try to import pynput components, handle import errors gracefully
try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode
    PYNPUT_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"pynput not available: {e}")
    PYNPUT_AVAILABLE = False
    # Create dummy classes for testing
    class Key:
        ctrl_l = 'ctrl_l'
        ctrl_r = 'ctrl_r'
        shift_l = 'shift_l'
        shift_r = 'shift_r'
        alt_l = 'alt_l'
        alt_r = 'alt_r'
    
    class KeyCode:
        @staticmethod
        def from_char(char):
            return f'key_{char}'
    
    class keyboard:
        class Listener:
            def __init__(self, on_press=None, on_release=None):
                self.on_press = on_press
                self.on_release = on_release
                self.running = False
            
            def start(self):
                raise ImportError("pynput not available")
            
            def stop(self):
                pass

logger = logging.getLogger(__name__)


class LinuxKeyboardListener(IKeyboardListener):
    """
    Linux implementation of IKeyboardListener using pynput for global hotkey detection.
    
    This class listens for the Ctrl+Shift+Alt+A hotkey combination and publishes
    events to the output queue when detected. It toggles between start and stop
    recording events.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        output_queue: Optional[QueueProtocol] = None,
    ):
        """Initialize Linux keyboard listener with pynput integration."""
        self._config = config or {}
        self._output_queue = output_queue if output_queue else asyncio.Queue()
        self._running = False
        self._listener = None
        self._current_keys = set()
        self._target_hotkey = {Key.ctrl_l, Key.shift_l, Key.alt_l, KeyCode.from_char('a')}
        
        # Alternative keys for right-side modifiers
        self._target_hotkey_alt = {Key.ctrl_r, Key.shift_r, Key.alt_r, KeyCode.from_char('a')}
        
        # Toggle state for recording
        self._recording_state = False
        
        logger.info(
            f"LinuxKeyboardListener initialized with config: {self._config}, "
            f"using output_queue: {id(self._output_queue)}"
        )

    @property
    def output_queue(self) -> QueueProtocol:
        """Return the output queue for publishing detected hotkey events."""
        return self._output_queue

    def _on_press(self, key):
        """Handle key press events from pynput listener."""
        try:
            self._current_keys.add(key)
            
            # Check if our target hotkey combination is pressed
            if self._is_target_hotkey_pressed():
                # Use asyncio.create_task to schedule the coroutine
                asyncio.create_task(self._send_hotkey_event())
                logger.info("LinuxKeyboardListener detected hotkey: Ctrl+Shift+Alt+A")
                
        except Exception as e:
            logger.error(f"LinuxKeyboardListener error in _on_press: {e}")

    def _on_release(self, key):
        """Handle key release events from pynput listener."""
        try:
            # Remove the key from current pressed keys
            self._current_keys.discard(key)
        except Exception as e:
            logger.error(f"LinuxKeyboardListener error in _on_release: {e}")

    def _is_target_hotkey_pressed(self) -> bool:
        """Check if the target hotkey combination is currently pressed."""
        # Check for left-side modifiers + 'a'
        left_combo = {Key.ctrl_l, Key.shift_l, Key.alt_l, KeyCode.from_char('a')}
        # Check for right-side modifiers + 'a'
        right_combo = {Key.ctrl_r, Key.shift_r, Key.alt_r, KeyCode.from_char('a')}
        # Check for mixed modifiers + 'a'
        mixed_combo_1 = {Key.ctrl_l, Key.shift_l, Key.alt_r, KeyCode.from_char('a')}
        mixed_combo_2 = {Key.ctrl_r, Key.shift_l, Key.alt_l, KeyCode.from_char('a')}
        
        return (
            left_combo.issubset(self._current_keys) or
            right_combo.issubset(self._current_keys) or
            mixed_combo_1.issubset(self._current_keys) or
            mixed_combo_2.issubset(self._current_keys)
        )

    async def _send_hotkey_event(self):
        """Send hotkey event to output queue, toggling between start and stop recording."""
        try:
            # Toggle recording state
            if self._recording_state:
                hotkey_event = "ctrl+shift+stop_recording"
                self._recording_state = False
            else:
                hotkey_event = "ctrl+shift+start_recording"
                self._recording_state = True
                
            await self._output_queue.put(hotkey_event)
            logger.info(f"LinuxKeyboardListener sent event: {hotkey_event}")
        except Exception as e:
            logger.error(f"LinuxKeyboardListener error sending event: {e}")

    async def run(self) -> None:
        """
        Main async loop to listen for keyboard input and post events to output_queue.
        """
        logger.info("LinuxKeyboardListener.run() started")
        self._running = True

        try:
            # Start the pynput listener in a separate thread
            if not PYNPUT_AVAILABLE:
                logger.warning("pynput not available, using fallback mode")
                # Fallback: send a test event after 5 seconds
                await asyncio.sleep(5.0)
                if self._running:
                    await self._output_queue.put("ctrl+shift+start_recording")
                    logger.info("LinuxKeyboardListener sent fallback event")
                return
                
            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            
            # Start the listener in a separate thread
            self._listener.start()
            logger.info("LinuxKeyboardListener: pynput listener started")
            
            # Keep the async task running while the listener is active
            while self._running and self._listener.running:
                await asyncio.sleep(0.1)  # Small sleep to prevent busy waiting
                
        except Exception as e:
            logger.error(f"LinuxKeyboardListener.run() error: {e}")
            # If pynput fails, fall back to a simple event for testing
            if self._running:
                await asyncio.sleep(5.0)  # Wait a bit before sending fallback event
                if self._running:
                    await self._output_queue.put("ctrl+shift+start_recording")
                    logger.info("LinuxKeyboardListener sent fallback event")
            raise
        except asyncio.CancelledError:
            logger.info("LinuxKeyboardListener.run() cancelled")
            self._running = False
            raise
        finally:
            # Clean up the listener
            if self._listener:
                self._listener.stop()
                logger.info("LinuxKeyboardListener: pynput listener stopped")
            logger.info("LinuxKeyboardListener.run() stopped")

    def stop(self) -> None:
        """Stop the keyboard listener."""
        self._running = False
        if self._listener:
            self._listener.stop()
        logger.info("LinuxKeyboardListener stop requested")