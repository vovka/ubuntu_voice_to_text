import os


class Config:
    MODEL_PATH = os.path.expanduser("/models/vosk-model-small-en-us-0.15")
    SAMPLE_RATE = 16000

    @property
    def HOTKEY_COMBO(self):
        try:
            from pynput import keyboard

            return {keyboard.Key.cmd, keyboard.Key.shift}  # Win+Shift
        except ImportError:
            # Fallback for testing without dependencies
            return set()
