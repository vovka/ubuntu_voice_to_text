from .config import Config
from .interfaces.state_manager import StateManager, VoiceTypingState


class HotkeyManager:
    def __init__(
        self, config: Config, state_ref, tray_icon_manager, audio_processor=None, state_manager: StateManager = None
    ):
        self.config = config
        self.state_ref = state_ref
        self.tray_icon_manager = tray_icon_manager
        self.audio_processor = audio_processor
        self.state_manager = state_manager
        self._combo_pressed = False  # Track if combo was pressed

    def on_press(self, key):
        if key in self.config.HOTKEY_COMBO:
            self.state_ref.current_keys.add(key)
        # Set flag if combo is pressed down
        if self.state_ref.current_keys == self.config.HOTKEY_COMBO:
            self._combo_pressed = True

    def on_release(self, key):
        if key in self.state_ref.current_keys:
            self.state_ref.current_keys.remove(key)
        # If we're currently listening and any combo key is released, stop listening
        if self.state_ref.state == "listening" and key in self.config.HOTKEY_COMBO:
            print("[HotkeyManager] HOTKEY_COMBO released while listening")
            self._combo_pressed = False  # Reset the flag to prevent starting again
            self.set_state("finish_listening")
        # If not listening and combo was pressed and all keys released,
        # start listening
        elif (
            self.state_ref.state != "listening"
            and self._combo_pressed
            and not self.state_ref.current_keys
        ):
            self._combo_pressed = False
            print("[HotkeyManager] HOTKEY_COMBO released, activating listening")
            self.set_state("listening")

    def set_state(self, new_state):
        print(f"[HotkeyManager] set_state({new_state}) called")
        
        # Use StateManager if available, otherwise fall back to direct mutation
        if self.state_manager is not None:
            try:
                # Convert string to VoiceTypingState enum
                if isinstance(new_state, str):
                    new_state_enum = VoiceTypingState(new_state)
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
                    if self.tray_icon_manager:
                        self.tray_icon_manager.update_icon()
                else:
                    print(f"[HotkeyManager] Failed to transition to state: {new_state_enum}")
            except ValueError as e:
                print(f"[HotkeyManager] Invalid state: {new_state}, error: {e}")
        else:
            # Fallback to direct state mutation for backward compatibility
            if self.state_ref.state != new_state:
                self.state_ref.state = new_state
                print(f"[HotkeyManager] Voice typing state: {self.state_ref.state}")
                # Reset listening timer when starting to listen (requirement: timer reset)
                if new_state == "listening" and self.audio_processor:
                    self.audio_processor.start_listening()
                if self.tray_icon_manager:
                    self.tray_icon_manager.update_icon()

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
