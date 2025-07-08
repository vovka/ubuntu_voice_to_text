"""Linux keyboard listener using pynput HotKey for robust hotkey detection."""

import asyncio
from typing import Any, Dict, Optional

from interfaces.keyboard_listener import IKeyboardListener
from interfaces.queue_protocol import QueueProtocol
from .hotkey_handler import HotkeyHandler, PYNPUT_AVAILABLE
from .event_manager import EventManager
from .fallback_handler import FallbackHandler
from .legacy_methods import LegacyMethods, Key, KeyCode


class LinuxKeyboardListener(IKeyboardListener):
    """Linux keyboard listener using pynput HotKey for robust detection."""

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 output_queue: Optional[QueueProtocol] = None,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        """Initialize with component handlers."""
        self._config = config or {}
        self._output_queue = output_queue if output_queue else asyncio.Queue()
        self._running = False
        self._listener = None  # Legacy compatibility
        self._setup_components()

    def _setup_components(self):
        """Setup component handlers."""
        self._event_manager = EventManager(self._output_queue)
        self._hotkey_handler = HotkeyHandler(self._event_manager.send_toggle_event)
        self._fallback_handler = FallbackHandler(self._event_manager)
        self._legacy = LegacyMethods(self._event_manager)

    @property
    def output_queue(self) -> QueueProtocol:
        """Return the output queue."""
        return self._output_queue

    async def run(self) -> None:
        """Main async loop to listen for keyboard input."""
        self._running = True
        try:
            if not PYNPUT_AVAILABLE:
                await self._run_fallback_mode()
            else:
                await self._run_hotkey_mode()
        except asyncio.CancelledError:
            raise
        finally:
            self._cleanup()

    async def _run_fallback_mode(self) -> None:
        """Run fallback mode when pynput unavailable."""
        self._fallback_handler.start()
        await self._fallback_handler.run_fallback_mode()

    async def _run_hotkey_mode(self) -> None:
        """Run with pynput hotkey detection."""
        loop = asyncio.get_running_loop()
        self._hotkey_handler.setup_hotkey(loop)
        self._hotkey_handler.start_listener()
        while self._running:
            await asyncio.sleep(0.1)

    def _cleanup(self) -> None:
        """Cleanup resources."""
        self._running = False
        self._hotkey_handler.stop_listener()
        self._fallback_handler.stop()

    def stop(self) -> None:
        """Stop the keyboard listener."""
        self._cleanup()

    # Legacy interface delegation
    def _on_press(self, key):
        self._legacy.on_press(key)
    def _on_release(self, key):
        self._legacy.on_release(key)
    def _is_target_hotkey_pressed(self) -> bool:
        return self._legacy.is_target_hotkey_pressed()
    async def _send_hotkey_event(self):
        await self._legacy.send_hotkey_event()

    @property
    def _current_keys(self):
        return self._legacy.current_keys

    @_current_keys.setter
    def _current_keys(self, value):
        self._legacy._current_keys = value

    @property
    def _recording_state(self):
        return self._event_manager._recording_state

    @_recording_state.setter
    def _recording_state(self, value):
        self._event_manager._recording_state = value
