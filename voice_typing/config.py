import os


class Config:
    @property
    def MODEL_PATH(self):
        """Get model path from environment variable or use default."""
        return os.getenv(
            "VOSK_MODEL_PATH", os.path.expanduser("/models/vosk-model-small-en-us-0.15")
        )

    SAMPLE_RATE = 16000

    @property
    def RECOGNITION_SOURCE(self):
        """Get recognition source from environment variable, default to 'vosk'."""
        return os.getenv("RECOGNITION_SOURCE", "vosk")

    @property
    def OPENAI_API_KEY(self):
        """Get OpenAI API key from environment variable."""
        return os.getenv("OPENAI_API_KEY")

    @property
    def WHISPER_MODEL(self):
        """Get Whisper model from environment variable, default to 'whisper-1'."""
        return os.getenv("WHISPER_MODEL", "whisper-1")

    @property
    def HOTKEY_COMBO(self):
        try:
            from pynput import keyboard

            return {keyboard.Key.cmd, keyboard.Key.shift}  # Win+Shift
        except ImportError:
            # Fallback for testing without dependencies
            return set()
