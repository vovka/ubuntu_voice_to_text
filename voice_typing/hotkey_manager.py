from .config import Config


class HotkeyManager:
    def __init__(self, config: Config, state_ref, tray_icon_manager, audio_processor=None):
        self.config = config
        self.state_ref = state_ref
        self.tray_icon_manager = tray_icon_manager
        self.audio_processor = audio_processor
        self._combo_pressed = False  # Track if combo was pressed

    def on_press(self, key):
        if hasattr(self.config, 'HOTKEY_COMBO') and key in self.config.HOTKEY_COMBO:
            self.state_ref.current_keys.add(key)
        # Set flag if combo is pressed down
        if hasattr(self.config, 'HOTKEY_COMBO') and self.state_ref.current_keys == self.config.HOTKEY_COMBO:
            self._combo_pressed = True

    def on_release(self, key):
        if key in self.state_ref.current_keys:
            self.state_ref.current_keys.remove(key)
        # If we're currently listening and any combo key is released, stop listening
        if self.state_ref.state == 'listening' and hasattr(self.config, 'HOTKEY_COMBO') and key in self.config.HOTKEY_COMBO:
            print("[HotkeyManager] HOTKEY_COMBO released while listening")
            self._combo_pressed = False  # Reset the flag to prevent starting again
            self.set_state('finish_listening')
        # If not listening and combo was pressed and all keys are now released, start listening
        elif (
            self.state_ref.state != 'listening'
            and self._combo_pressed
            and not self.state_ref.current_keys
        ):
            self._combo_pressed = False
            print("[HotkeyManager] HOTKEY_COMBO released, activating listening")
            self.set_state('listening')

    def set_state(self, new_state):
        print(f"[HotkeyManager] set_state({new_state}) called")
        if self.state_ref.state != new_state:
            self.state_ref.state = new_state
            print(f"[HotkeyManager] Voice typing state: {self.state_ref.state}")
            # Reset listening timer when starting to listen (requirement: timer reset)
            if new_state == 'listening' and self.audio_processor:
                self.audio_processor.start_listening()
            self.tray_icon_manager.update_icon()

    def hotkey_thread(self):
        print("[HotkeyManager] Starting hotkey listener thread")
        try:
            from pynput import keyboard
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                listener.join()
        except ImportError:
            print("[HotkeyManager] pynput not available, hotkey functionality disabled")
