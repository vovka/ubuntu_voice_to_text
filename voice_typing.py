import os
import queue
import json
import threading
import subprocess
import time
import sys

import sounddevice as sd
import vosk
from pynput import keyboard
import pystray
from PIL import Image, ImageDraw


# --- System Tray Icon ---
class TrayIconManager:
    def __init__(self, state_ref):
        self.state_ref = state_ref
        self.icon = None

    def create_image_text(self, state="idle"):
        width, height = 32, 32
        image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        dc = ImageDraw.Draw(image)

        if state == "finish_listening":
            color = (40, 150, 150)  # blue
        elif state == "listening":
            color = (40, 255, 40)  # green
        else:
            color = (120, 120, 120)  # grey

        # Draw a filled circle
        dc.ellipse(
            [(4, 4), (width - 4, height - 4)], fill=color, outline=(60, 60, 60), width=2
        )

        return image

    def update_icon(self):
        if self.icon:
            print(f"[TrayIconManager] Updating icon: state={self.state_ref.state}")
            self.icon.icon = self.create_image_text(self.state_ref.state)
            if self.state_ref.state == "finish_listening":
                self.icon.title = "Voice Typing: finish_listening"
            elif self.state_ref.state == "listening":
                self.icon.title = "Voice Typing: ON"
            else:
                self.icon.title = "Voice Typing: OFF"

    def exit_application(self, icon, item):
        """Exit the application cleanly."""
        print("[TrayIconManager] Exit requested from tray menu")
        icon.stop()
        os._exit(0)

    def tray_thread(self):
        print("[TrayIconManager] Starting tray icon thread")
        # Create menu with Exit item
        menu = pystray.Menu(
            pystray.MenuItem('Exit', self.exit_application)
        )
        self.icon = pystray.Icon('voice_typing', menu=menu)
        self.state_ref.icon = self.icon
        self.update_icon()
        self.icon.run()


# --- Configuration ---
class Config:
    MODEL_PATH = os.path.expanduser("/opt/vosk-model-small-en-us-0.15")
    SAMPLE_RATE = 16000
    HOTKEY_COMBO = {keyboard.Key.ctrl, keyboard.Key.shift}


# --- Hotkey Listener ---
class HotkeyManager:
    def __init__(self, config: Config, state_ref, tray_icon_manager):
        self.config = config
        self.state_ref = state_ref
        self.tray_icon_manager = tray_icon_manager

    def on_press(self, key):
        if key in self.config.HOTKEY_COMBO:
            self.state_ref.current_keys.add(key)
        if (
            self.state_ref.current_keys == self.config.HOTKEY_COMBO
            and self.state_ref.state != "listening"
        ):
            print("[HotkeyManager] HOTKEY_COMBO pressed")
            self.set_state("listening")

    def on_release(self, key):
        if key in self.state_ref.current_keys:
            self.state_ref.current_keys.remove(key)
        if (
            self.state_ref.state == "listening"
            and not self.state_ref.current_keys.issuperset(self.config.HOTKEY_COMBO)
        ):
            print("[HotkeyManager] HOTKEY_COMBO released")
            self.set_state("finish_listening")

    def set_state(self, new_state):
        print(f"[HotkeyManager] set_state({new_state}) called")
        if self.state_ref.state != new_state:
            self.state_ref.state = new_state
            print(f"[HotkeyManager] Voice typing state: {self.state_ref.state}")
            self.tray_icon_manager.update_icon()

    def hotkey_thread(self):
        print("[HotkeyManager] Starting hotkey listener thread")
        with keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        ) as listener:
            listener.join()


# --- Global State ---
class GlobalState:
    q = queue.Queue()
    state = "idle"  # 'idle', 'listening', 'finish_listening'
    icon = None
    current_keys = set()


# --- Vosk Speech Recognition & Typing Automation ---
class AudioProcessor:
    def __init__(self, config: Config, state_ref: GlobalState):
        if not os.path.exists(config.MODEL_PATH):
            print(
                "[AudioProcessor] ❌ Vosk model not found. Download and extract it to:"
            )
            print(f"[AudioProcessor] {config.MODEL_PATH}")
            exit(1)
        self.state_ref = state_ref
        self.model = vosk.Model(config.MODEL_PATH)
        self.recognizer = vosk.KaldiRecognizer(self.model, config.SAMPLE_RATE)
        self.last_text_at = None

    def process_buffer(self, buffer):
        for chunk in buffer:
            self.recognizer.AcceptWaveform(chunk)
        result = json.loads(self.recognizer.Result())
        print(f"[AudioProcessor] Recognizer result (final): {result}")
        if result.get("text"):
            self.last_text_at = time.time()
            print(f"[AudioProcessor] 🗣️ {result['text']}")
            self.type_text(result["text"])
        if (
            self.state_ref.state == "finish_listening"
            and self.last_text_at is not None
            and time.time() - self.last_text_at > 5
        ):
            print("[AudioProcessor] finish_listening state: resetting to idle")
            self.state_ref.state = "idle"

    @staticmethod
    def type_text(text):
        subprocess.run(["xdotool", "type", text + " "])


# --- Voice Typing Main Loop ---
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
        if True:  # self.state_ref.state in ('listening', 'finish_listening'):
            state = self.state_ref.state
            print(
                f"[VoiceTyping] Audio callback: putting audio data in queue "
                f"(state={state})"
            )
            self.state_ref.q.put(bytes(indata))

    def voice_typing_loop(self):
        print("[VoiceTyping] Starting voice typing main loop")
        buffer = []
        with sd.RawInputStream(
            samplerate=self.config.SAMPLE_RATE,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self.audio_callback,
        ):
            print("[VoiceTyping] 🎤 Voice typing ready. Hold Ctrl+Shift to speak.")
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


# --- Main ---
if __name__ == "__main__":
    config = Config()
    state_ref = GlobalState()
    audio_processor = AudioProcessor(config, state_ref)
    tray_icon_manager = TrayIconManager(state_ref)
    hotkey_manager = HotkeyManager(config, state_ref, tray_icon_manager)
    voice_typing = VoiceTyping(config, state_ref, audio_processor, tray_icon_manager)

    # print("[trace] Starting tray and hotkey threads")
    threading.Thread(target=tray_icon_manager.tray_thread, daemon=True).start()
    threading.Thread(target=hotkey_manager.hotkey_thread, daemon=True).start()
    # Main thread: audio/voice typing
    voice_typing.voice_typing_loop()
