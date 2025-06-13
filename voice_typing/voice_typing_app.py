from .config import Config
from .audio_processor import AudioProcessor
from .tray_icon_manager import TrayIconManager


class VoiceTyping:
    def __init__(
        self,
        config: Config,
        state_ref,
        audio_processor: AudioProcessor,
        tray_icon_manager: TrayIconManager,
    ):
        self.config = config
        self.state_ref = state_ref
        self.audio_processor = audio_processor
        self.tray_icon_manager = tray_icon_manager

    def audio_callback(self, indata, frames, time, status):
        if self.state_ref.state in ("listening", "finish_listening"):
            print(
                f"[VoiceTyping] Audio callback: putting audio data in queue (state={self.state_ref.state})"
            )
            self.state_ref.q.put(bytes(indata))

    def voice_typing_loop(self):
        print("[VoiceTyping] Starting voice typing main loop")
        try:
            import sounddevice as sd

            buffer = []
            with sd.RawInputStream(
                samplerate=self.config.SAMPLE_RATE,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=self.audio_callback,
            ):
                print(
                    "[VoiceTyping] 🎤 Voice typing ready. Press and release Ctrl+Shift to start listening."
                )
                while True:
                    if self.state_ref.state == "idle":
                        sd.sleep(100)
                        continue

                    data = self.state_ref.q.get()
                    buffer.append(data)
                    self.audio_processor.process_buffer(buffer)
                    buffer.clear()
                    self.tray_icon_manager.update_icon()
                    # Only process and return text when state becomes idle (see above)
        except ImportError:
            print(
                "[VoiceTyping] ❌ sounddevice not available, audio functionality disabled"
            )
