import threading
import os

from voice_typing import (
    Config,
    AudioProcessor,
    TrayIconManager,
    HotkeyManager,
    PipelineVoiceTyping,
    BasicStateManager,
)

# --- Main ---
if __name__ == "__main__":
    config = Config()
    
    # Create modern state manager
    state_manager = BasicStateManager()
    
    # Add logging for all state transitions
    def log_state_transitions(transition):
        print(f"[StateManager] State transition: {transition.from_state.value} → {transition.to_state.value}")
        if transition.metadata:
            print(f"[StateManager] Transition metadata: {transition.metadata}")
    
    state_manager.register_state_listener(log_state_transitions)
    
    # Create TrayIconManager with StateManager subscription for decoupled UI
    def handle_exit():
        """Handle application exit cleanly."""
        print("[Main] Application exit requested")
        os._exit(0)
    
    tray_icon_manager = TrayIconManager(
        state_manager=state_manager,
        exit_callback=handle_exit
    )
    
    # Use pipeline-based voice typing system
    print("[Main] Using pipeline-based voice typing system")
    voice_typing = PipelineVoiceTyping(config, state_manager, tray_icon_manager)
    
    # Create audio processor for hotkey manager
    audio_processor = AudioProcessor(config, state_manager)
    
    hotkey_manager = HotkeyManager(
        config, state_manager, tray_icon_manager, audio_processor
    )

    # Start tray and hotkey threads
    threading.Thread(target=tray_icon_manager.tray_thread, daemon=True).start()
    threading.Thread(target=hotkey_manager.hotkey_thread, daemon=True).start()
    
    # Main thread: voice typing
    voice_typing.voice_typing_loop()
