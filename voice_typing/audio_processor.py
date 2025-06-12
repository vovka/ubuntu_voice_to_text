import sys
from typing import Optional

from .config import Config
from .global_state import GlobalState
from .recognition_sources import VoiceRecognitionSource, VoskRecognitionSource


class AudioProcessor:
    def __init__(
        self,
        config: Config,
        state_ref: GlobalState,
        recognition_source: Optional[VoiceRecognitionSource] = None,
    ):
        self.state_ref = state_ref

        # Use provided recognition source or default to Vosk
        if recognition_source is None:
            recognition_source = VoskRecognitionSource()

        self.recognition_source = recognition_source

        # Initialize the recognition source
        recognition_config = {
            "model_path": config.MODEL_PATH,
            "sample_rate": config.SAMPLE_RATE,
        }

        if not self.recognition_source.initialize(recognition_config):
            print("[AudioProcessor] ❌ Failed to initialize voice recognition source")
            sys.exit(1)

        self.last_text_at = None
        self.listening_started_at = None

    def start_listening(self):
        """Reset timers when listening starts to enable inactivity timeout"""
        import time

        self.listening_started_at = time.time()
        self.last_text_at = None
        print(f"[AudioProcessor] Listening started at {self.listening_started_at}")

    def process_buffer(self, buffer):
        if not self.recognition_source.is_available():
            return

        import time

        for chunk in buffer:
            self.recognition_source.process_audio_chunk(chunk)

        result = self.recognition_source.get_result()
        if result is None:
            return

        print(f"[AudioProcessor] Recognizer result (final): {result}")
        if result.get("text"):
            self.last_text_at = time.time()
            print(f"[AudioProcessor] 🗣️ {result['text']}")
            self.type_text(result["text"])

        # Auto-disable after 5 seconds of inactivity (requirement: inactivity timeout)
        current_time = time.time()

        # For 'listening' state: check if 5 seconds passed since last text OR start
        if (
            self.state_ref.state == "listening"
            and self.listening_started_at is not None
        ):
            time_since_last_activity = current_time - (
                self.last_text_at if self.last_text_at else self.listening_started_at
            )
            if time_since_last_activity > 5:
                print(
                    "[AudioProcessor] listening state: auto-disabling after "
                    "5 seconds of inactivity"
                )
                self.state_ref.state = "idle"

        # For 'finish_listening' state: existing timeout logic (manual stop flow)
        elif (
            self.state_ref.state == "finish_listening"
            and self.last_text_at is not None
            and current_time - self.last_text_at > 5
        ):
            print("[AudioProcessor] finish_listening state: resetting to idle")
            self.state_ref.state = "idle"

    @staticmethod
    def type_text(text):
        import subprocess

        subprocess.run(["xdotool", "type", text + " "])
