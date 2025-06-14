import threading
import os

from voice_typing import (
    Config,
    GlobalState,
    AudioProcessor,
    TrayIconManager,
    HotkeyManager,
    VoiceTyping,
)
from voice_typing.interfaces.state_manager import LegacyStateManagerAdapter

# --- Main ---
if __name__ == "__main__":
    config = Config()
    state_ref = GlobalState()
    
    # Create centralized state manager
    state_manager = LegacyStateManagerAdapter(state_ref)
    
    # Add logging for all state transitions
    def log_state_transitions(transition):
        print(f"[StateManager] State transition: {transition.from_state.value} → {transition.to_state.value}")
        if transition.metadata:
            print(f"[StateManager] Transition metadata: {transition.metadata}")
    
    state_manager.register_state_listener(log_state_transitions)
    
    audio_processor = AudioProcessor(config, state_ref)
    
    # Create TrayIconManager with StateManager subscription for decoupled UI
    def handle_exit():
        """Handle application exit cleanly."""
        print("[Main] Application exit requested")
        os._exit(0)
    
    tray_icon_manager = TrayIconManager(
        state_ref=state_ref,  # Legacy support
        state_manager=state_manager,  # New event-driven approach
        exit_callback=handle_exit
    )
    hotkey_manager = HotkeyManager(
        config, state_ref, tray_icon_manager, audio_processor, state_manager
    )
    voice_typing = VoiceTyping(config, state_ref, audio_processor, tray_icon_manager)

    # print("[trace] Starting tray and hotkey threads")
    threading.Thread(target=tray_icon_manager.tray_thread, daemon=True).start()
    threading.Thread(target=hotkey_manager.hotkey_thread, daemon=True).start()
    # Main thread: audio/voice typing
    voice_typing.voice_typing_loop()
