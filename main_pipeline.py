import threading
import os
import sys

from voice_typing import (
    Config,
    GlobalState,
    AudioProcessor,
    TrayIconManager,
    HotkeyManager,
    VoiceTyping,
    PipelineVoiceTyping,
)
from voice_typing.interfaces.state_manager import LegacyStateManagerAdapter

# --- Main ---
if __name__ == "__main__":
    # Check if we should use the pipeline system
    use_pipeline = "--pipeline" in sys.argv
    
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
    
    if use_pipeline:
        print("[Main] Using pipeline-based voice typing system")
        voice_typing = PipelineVoiceTyping(config, state_ref, tray_icon_manager)
    else:
        print("[Main] Using legacy voice typing system")
        audio_processor = AudioProcessor(config, state_ref)
        voice_typing = VoiceTyping(config, state_ref, audio_processor, tray_icon_manager)
    
    hotkey_manager = HotkeyManager(
        config, state_ref, tray_icon_manager, 
        getattr(voice_typing, 'audio_processor', None), 
        state_manager
    )

    # print("[trace] Starting tray and hotkey threads")
    threading.Thread(target=tray_icon_manager.tray_thread, daemon=True).start()
    threading.Thread(target=hotkey_manager.hotkey_thread, daemon=True).start()
    
    # Main thread: audio/voice typing
    voice_typing.voice_typing_loop()