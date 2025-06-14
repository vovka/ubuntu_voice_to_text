import sys
from typing import Optional

from .config import Config
from .global_state import GlobalState
from .recognition_sources import (
    VoiceRecognitionSource,
    VoskRecognitionSource,
    WhisperRecognitionSource,
)


class AudioProcessor:
    def __init__(
        self,
        config: Config,
        state_ref: GlobalState,
        recognition_source: Optional[VoiceRecognitionSource] = None,
    ):
        self.state_ref = state_ref

        # Use provided recognition source or create based on config
        if recognition_source is None:
            recognition_source = self._create_recognition_source(config)

        self.recognition_source = recognition_source

        # Initialize the recognition source
        recognition_config = self._get_recognition_config(config)

        if not self.recognition_source.initialize(recognition_config):
            print("[AudioProcessor] ❌ Failed to initialize voice recognition source")
            sys.exit(1)

        self.last_text_at = None
        self.listening_started_at = None

    def _create_recognition_source(self, config: Config) -> VoiceRecognitionSource:
        """Create recognition source based on configuration."""
        source_type = config.RECOGNITION_SOURCE.lower()

        if source_type == "whisper":
            return WhisperRecognitionSource()
        elif source_type == "vosk":
            return VoskRecognitionSource()
        else:
            print(
                f"[AudioProcessor] ⚠️ Unknown recognition source '{source_type}', "
                "defaulting to Vosk"
            )
            return VoskRecognitionSource()

    def _get_recognition_config(self, config: Config) -> dict:
        """Get configuration dictionary for the recognition source."""
        base_config = {
            "sample_rate": config.SAMPLE_RATE,
        }

        if config.RECOGNITION_SOURCE.lower() == "whisper":
            base_config.update(
                {
                    "api_key": config.OPENAI_API_KEY,
                    "model": config.WHISPER_MODEL,
                }
            )
        else:
            # Vosk configuration
            base_config.update(
                {
                    "model_path": config.MODEL_PATH,
                }
            )

        return base_config

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
                print("[StateManager] State transition: listening → idle (AudioProcessor auto-timeout)")
                self.state_ref.state = "idle"

        # For 'finish_listening' state: existing timeout logic (manual stop flow)
        elif (
            self.state_ref.state == "finish_listening"
            and self.last_text_at is not None
            and current_time - self.last_text_at > 5
        ):
            print("[AudioProcessor] finish_listening state: resetting to idle")
            print("[StateManager] State transition: finish_listening → idle (AudioProcessor timeout)")
            self.state_ref.state = "idle"

    @staticmethod
    def type_text(text):
        import subprocess

        subprocess.run(["xdotool", "type", text + " "])
