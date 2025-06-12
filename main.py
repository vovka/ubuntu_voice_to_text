import threading

from voice_typing import (
    Config,
    GlobalState,
    AudioProcessor,
    TrayIconManager,
    HotkeyManager,
    VoiceTyping
)

# --- Main ---
if __name__ == "__main__":
    config = Config()
    state_ref = GlobalState()
    audio_processor = AudioProcessor(config, state_ref)
    tray_icon_manager = TrayIconManager(state_ref)
    hotkey_manager = HotkeyManager(config, state_ref, tray_icon_manager, audio_processor)
    voice_typing = VoiceTyping(config, state_ref, audio_processor, tray_icon_manager)

    # print("[trace] Starting tray and hotkey threads")
    threading.Thread(target=tray_icon_manager.tray_thread, daemon=True).start()
    threading.Thread(target=hotkey_manager.hotkey_thread, daemon=True).start()
    # Main thread: audio/voice typing
    voice_typing.voice_typing_loop()
