"""
Hotkey handler for Linux keyboard listener using pynput.keyboard.HotKey.

This module provides robust hotkey detection that works correctly across
different keyboard layouts and Docker environments.
"""

import asyncio
import logging
from typing import Optional

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    # Create dummy for testing
    class keyboard:
        class HotKey:
            def __init__(self, keys, on_activate):
                self.keys = keys
                self.on_activate = on_activate
    
        class Listener:
            def __init__(self, on_press=None, on_release=None):
                pass
            def start(self):
                raise ImportError("pynput not available")
            def stop(self):
                pass

logger = logging.getLogger(__name__)


class HotkeyHandler:
    """
    Handles hotkey detection using pynput.keyboard.HotKey for robust detection.
    
    Uses physical key detection instead of character mapping to avoid issues
    with different keyboard layouts in Docker environments.
    """

    def __init__(self, hotkey_callback):
        """Initialize hotkey handler with callback function."""
        self._hotkey_callback = hotkey_callback
        self._hotkey = None
        self._listener = None
        self._loop = None

    def setup_hotkey(self, loop: asyncio.AbstractEventLoop) -> None:
        """Setup the hotkey listener with asyncio loop."""
        self._loop = loop
        if not PYNPUT_AVAILABLE:
            logger.warning("pynput not available for hotkey detection")
            return

        # Use HotKey for robust detection
        self._hotkey = keyboard.HotKey(
            {keyboard.Key.ctrl, keyboard.Key.shift, keyboard.Key.alt, 
             keyboard.KeyCode.from_char('a')},
            self._on_hotkey_detected
        )

    def _on_hotkey_detected(self) -> None:
        """Handle hotkey detection and bridge to asyncio."""
        if self._loop and self._hotkey_callback:
            asyncio.run_coroutine_threadsafe(
                self._hotkey_callback(), self._loop
            )

    def start_listener(self) -> None:
        """Start the keyboard listener."""
        if not PYNPUT_AVAILABLE or not self._hotkey:
            raise ImportError("pynput not available")

        self._listener = keyboard.Listener(
            on_press=self._hotkey.press,
            on_release=self._hotkey.release
        )
        self._listener.start()

    def stop_listener(self) -> None:
        """Stop the keyboard listener."""
        if self._listener:
            self._listener.stop()
            self._listener = None