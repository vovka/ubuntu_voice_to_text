from .config import Config
from .interfaces.state_manager import StateManager, VoiceTypingState


class HotkeyManager:
    def __init__(
        self, config: Config, state_manager: StateManager, tray_icon_manager=None, audio_processor=None
    ):
        self.config = config
        self.state_manager = state_manager
        self.tray_icon_manager = tray_icon_manager
        self.audio_processor = audio_processor
        self._combo_pressed = False  # Track if combo was pressed
        self._current_keys = set()  # Track currently pressed keys

    def on_press(self, key):
        if key in self.config.HOTKEY_COMBO:
            self._current_keys.add(key)
        # Set flag if combo is pressed down
        if self._current_keys == self.config.HOTKEY_COMBO:
            self._combo_pressed = True

    def on_release(self, key):
        if key in self._current_keys:
            self._current_keys.remove(key)
        
        current_state = self.state_manager.get_current_state()
        
        # If we're currently listening and any combo key is released, stop listening
        if current_state == VoiceTypingState.LISTENING and key in self.config.HOTKEY_COMBO:
            print("[HotkeyManager] HOTKEY_COMBO released while listening")
            self._combo_pressed = False  # Reset the flag to prevent starting again
            self.set_state(VoiceTypingState.FINISH_LISTENING)
        # If not listening and combo was pressed and all keys released,
        # start listening
        elif (
            current_state != VoiceTypingState.LISTENING
            and self._combo_pressed
            and not self._current_keys
        ):
            self._combo_pressed = False
            print("[HotkeyManager] HOTKEY_COMBO released, activating listening")
            self.set_state(VoiceTypingState.LISTENING)

    def set_state(self, new_state):
        print(f"[HotkeyManager] set_state({new_state}) called")
        
        # Convert string to VoiceTypingState enum if needed
        if isinstance(new_state, str):
            try:
                new_state_enum = VoiceTypingState(new_state)
            except ValueError as e:
                print(f"[HotkeyManager] Invalid state: {new_state}, error: {e}")
                return
        else:
            new_state_enum = new_state
        
        # Use StateManager for controlled state transitions
        success = self.state_manager.set_state(new_state_enum, 
                                             metadata={'source': 'hotkey_manager'})
        if success:
            print(f"[HotkeyManager] Voice typing state: {new_state_enum.value}")
            # Reset listening timer when starting to listen (requirement: timer reset)
            if new_state_enum == VoiceTypingState.LISTENING and self.audio_processor:
                self.audio_processor.start_listening()
        else:
            print(f"[HotkeyManager] Failed to transition to state: {new_state_enum}")

    def hotkey_thread(self):
        print("[HotkeyManager] Starting hotkey listener thread")
        try:
            from pynput import keyboard

            with keyboard.Listener(
                on_press=self.on_press, on_release=self.on_release
            ) as listener:
                listener.join()
        except ImportError:
            print(
                "[HotkeyManager] ❌ pynput not available, hotkey functionality disabled"
            )
