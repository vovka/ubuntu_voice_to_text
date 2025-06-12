import os
import sys

from .config import Config
from .global_state import GlobalState


class AudioProcessor:
    def __init__(self, config: Config, state_ref: GlobalState):
        if not os.path.exists(config.MODEL_PATH):
            print("[AudioProcessor] ❌ Vosk model not found. Download and extract it to:")
            print(f"[AudioProcessor] {config.MODEL_PATH}")
            sys.exit(1)
        self.state_ref = state_ref
        
        try:
            import vosk
            self.model = vosk.Model(config.MODEL_PATH)
            self.recognizer = vosk.KaldiRecognizer(self.model, config.SAMPLE_RATE)
        except ImportError:
            print("[AudioProcessor] vosk not available, audio processing disabled")
            self.model = None
            self.recognizer = None
            
        self.last_text_at = None
        self.listening_started_at = None

    def start_listening(self):
        """Reset timers when listening starts to enable inactivity timeout"""
        import time
        self.listening_started_at = time.time()
        self.last_text_at = None
        print(f"[AudioProcessor] Listening started at {self.listening_started_at}")

    def process_buffer(self, buffer):
        if not self.recognizer:
            return
            
        import json
        import time
        
        for chunk in buffer:
            self.recognizer.AcceptWaveform(chunk)
        result = json.loads(self.recognizer.Result())
        print(f"[AudioProcessor] Recognizer result (final): {result}")
        if result.get("text"):
            self.last_text_at = time.time()
            print(f"[AudioProcessor] 🗣️ {result['text']}")
            self.type_text(result["text"])
        
        # Auto-disable after 5 seconds of inactivity (requirement: inactivity timeout)
        current_time = time.time()
        
        # For 'listening' state: check if 5 seconds passed since last text OR listening start
        if self.state_ref.state == 'listening' and self.listening_started_at is not None:
            time_since_last_activity = current_time - (self.last_text_at if self.last_text_at else self.listening_started_at)
            if time_since_last_activity > 5:
                print("[AudioProcessor] listening state: auto-disabling after 5 seconds of inactivity")
                self.state_ref.state = 'idle'
        
        # For 'finish_listening' state: existing timeout logic (preserved for manual stop flow)
        elif self.state_ref.state == 'finish_listening' and self.last_text_at is not None and current_time - self.last_text_at > 5:
            print("[AudioProcessor] finish_listening state: resetting to idle")
            self.state_ref.state = 'idle'

    @staticmethod
    def type_text(text):
        import subprocess
        subprocess.run(["xdotool", "type", text + " "])