"""
Legacy compatibility methods for LinuxKeyboardListener tests.

These methods maintain backward compatibility with existing tests while
the main implementation uses the new HotKey-based approach.
"""

from typing import Set, Any

# Export for backward compatibility with tests
try:
    from pynput.keyboard import Key, KeyCode
except ImportError:
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


class LegacyMethods:
    """Legacy methods for test compatibility."""
    
    def __init__(self, event_manager):
        """Initialize with event manager reference."""
        self._event_manager = event_manager
        self._current_keys = set()

    def on_press(self, key):
        """Legacy test compatibility method."""
        self._current_keys.add(key)

    def on_release(self, key):
        """Legacy test compatibility method."""
        self._current_keys.discard(key)

    def is_target_hotkey_pressed(self) -> bool:
        """Legacy test compatibility method."""
        combos = [
            {Key.ctrl_l, Key.shift_l, Key.alt_l, KeyCode.from_char('a')},
            {Key.ctrl_r, Key.shift_r, Key.alt_r, KeyCode.from_char('a')},
            {Key.ctrl_l, Key.shift_l, Key.alt_r, KeyCode.from_char('a')},
            {Key.ctrl_r, Key.shift_l, Key.alt_l, KeyCode.from_char('a')}
        ]
        return any(combo.issubset(self._current_keys) for combo in combos)

    async def send_hotkey_event(self):
        """Legacy test compatibility method."""
        await self._event_manager.send_toggle_event()

    @property
    def current_keys(self) -> Set[Any]:
        """Expose current keys for testing."""
        return self._current_keys