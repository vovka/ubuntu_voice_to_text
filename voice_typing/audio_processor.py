import sys
from typing import Optional

from .config import Config
from .interfaces.state_manager import StateManager, VoiceTypingState
from .recognition_sources import (
    VoiceRecognitionSource,
    RecognitionSourceFactory,
)
from .interfaces.output_action import OutputDispatcher, KeyboardOutputActionTarget


class AudioProcessor:
    def __init__(
        self,
        config: Config,
        state_manager: StateManager,
        recognition_source: Optional[VoiceRecognitionSource] = None,
        output_dispatcher: Optional[OutputDispatcher] = None,
    ):
        self.state_manager = state_manager

        # Use provided recognition source or create based on config
        if recognition_source is None:
            recognition_source = RecognitionSourceFactory.create_recognition_source(config)

        self.recognition_source = recognition_source

        # Initialize the recognition source
        recognition_config = RecognitionSourceFactory.get_recognition_config(config)

        if not self.recognition_source.initialize(recognition_config):
            print("[AudioProcessor] ❌ Failed to initialize voice recognition source")
            sys.exit(1)

        # Set up output dispatcher
        if output_dispatcher is None:
            output_dispatcher = OutputDispatcher()
            output_dispatcher.initialize()
            
            # Add default keyboard output target
            keyboard_target = KeyboardOutputActionTarget()
            if keyboard_target.initialize({}):
                output_dispatcher.add_target(keyboard_target)
            else:
                print("[AudioProcessor] ⚠️ Warning: Keyboard output target not available")
        
        self.output_dispatcher = output_dispatcher

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

        # Auto-disable after 5 seconds of inactivity (requirement: inactivity timeout)
        # IMPORTANT: Check timeout before getting result to ensure it runs even when no result is available
        current_time = time.time()
        current_state = self.state_manager.get_current_state()

        # For 'listening' state: check if 5 seconds passed since last text OR start
        if (
            current_state == VoiceTypingState.LISTENING
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
                self.state_manager.set_state(VoiceTypingState.IDLE, 
                                           metadata={'source': 'audio_processor_timeout'})

        # For 'finish_listening' state: existing timeout logic (manual stop flow)
        elif (
            current_state == VoiceTypingState.FINISH_LISTENING
            and self.last_text_at is not None
            and current_time - self.last_text_at > 5
        ):
            print("[AudioProcessor] finish_listening state: resetting to idle")
            self.state_manager.set_state(VoiceTypingState.IDLE,
                                       metadata={'source': 'audio_processor_finish_timeout'})

        result = self.recognition_source.get_result()
        if result is None:
            return

        print(f"[AudioProcessor] Recognizer result (final): {result}")
        if result.get("text"):
            self.last_text_at = time.time()
            print(f"[AudioProcessor] 🗣️ {result['text']}")
            
            # Dispatch text through output dispatcher
            metadata = {
                'confidence': result.get('confidence', 0.0),
                'timestamp': self.last_text_at,
                'source': 'AudioProcessor'
            }
            self.output_dispatcher.dispatch_text(result["text"], metadata)
