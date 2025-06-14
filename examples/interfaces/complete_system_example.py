"""
Complete example showing all module interfaces working together.

This demonstrates how the four main interfaces can be composed
to create a complete voice typing system with proper decoupling.
"""

import time
from typing import Dict, Any, Optional, Callable

# Import all the interfaces
from voice_typing.interfaces import (
    AudioInputSource,
    OutputActionTarget,
    OutputType,
    StateManager,
    VoiceTypingState,
    StateTransition,
    VoiceRecognitionSource,
)
from voice_typing.interfaces.state_manager import BasicStateManager
from voice_typing.interfaces.output_action import CallbackOutputActionTarget


class MockAudioInput(AudioInputSource):
    """Mock audio input for demonstration."""
    
    def __init__(self):
        self._capturing = False
        self._callback = None
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        print("[MockAudioInput] Initialized")
        return True
    
    def start_capture(self, callback: Callable[[bytes], None]) -> bool:
        self._callback = callback
        self._capturing = True
        print("[MockAudioInput] Started capture")
        return True
    
    def stop_capture(self) -> None:
        self._capturing = False
        self._callback = None
        print("[MockAudioInput] Stopped capture")
    
    def is_capturing(self) -> bool:
        return self._capturing
    
    def is_available(self) -> bool:
        return True
    
    def cleanup(self) -> None:
        self.stop_capture()
    
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        return {"name": "Mock Microphone", "channels": 1}
    
    def simulate_audio(self, audio_data: bytes):
        """Simulate receiving audio data."""
        if self._callback and self._capturing:
            self._callback(audio_data)


class MockRecognitionSource(VoiceRecognitionSource):
    """Mock recognition source for demonstration."""
    
    def __init__(self):
        self._audio_chunks = []
        self._results = []
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        print("[MockRecognitionSource] Initialized")
        return True
    
    def process_audio_chunk(self, audio_chunk: bytes) -> None:
        self._audio_chunks.append(audio_chunk)
        # Simulate processing delay and result
        if len(self._audio_chunks) >= 3:  # After 3 chunks, produce result
            result = {
                'text': 'hello world',
                'confidence': 0.95,
                'final': True
            }
            self._results.append(result)
            self._audio_chunks.clear()
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        return self._results.pop(0) if self._results else None
    
    def is_available(self) -> bool:
        return True
    
    def cleanup(self) -> None:
        self._audio_chunks.clear()
        self._results.clear()


class MockOutputTarget(OutputActionTarget):
    """Mock output target for demonstration."""
    
    def __init__(self):
        self._delivered_texts = []
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        print("[MockOutputTarget] Initialized")
        return True
    
    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        self._delivered_texts.append(text)
        print(f"[MockOutputTarget] Delivered: '{text}'")
        return True
    
    def is_available(self) -> bool:
        return True
    
    def get_output_type(self) -> OutputType:
        return OutputType.CALLBACK
    
    def supports_formatting(self) -> bool:
        return False
    
    def cleanup(self) -> None:
        self._delivered_texts.clear()


class IntegratedVoiceTypingSystem:
    """
    Complete voice typing system using all interfaces.
    
    This demonstrates how the interfaces work together to create
    a modular, decoupled voice typing system.
    """
    
    def __init__(self,
                 audio_input: AudioInputSource,
                 recognition_source: VoiceRecognitionSource,
                 output_target: OutputActionTarget,
                 state_manager: StateManager):
        
        self.audio_input = audio_input
        self.recognition_source = recognition_source
        self.output_target = output_target
        self.state_manager = state_manager
        
        # Register for state changes
        self.state_manager.register_state_listener(self._on_state_change)
        
        print("[System] Integrated voice typing system initialized")
    
    def initialize(self) -> bool:
        """Initialize all subsystems."""
        print("[System] Initializing subsystems...")
        
        # Initialize all components
        audio_config = {'sample_rate': 16000, 'channels': 1}
        recognition_config = {'model': 'test'}
        output_config = {}
        
        if not self.audio_input.initialize(audio_config):
            print("[System] Failed to initialize audio input")
            return False
            
        if not self.recognition_source.initialize(recognition_config):
            print("[System] Failed to initialize recognition source")
            return False
            
        if not self.output_target.initialize(output_config):
            print("[System] Failed to initialize output target")
            return False
        
        print("[System] All subsystems initialized successfully")
        return True
    
    def _on_state_change(self, transition: StateTransition):
        """Handle state changes by coordinating subsystems."""
        print(f"[System] State: {transition.from_state.value} → {transition.to_state.value}")
        
        new_state = transition.to_state
        
        if new_state == VoiceTypingState.LISTENING:
            self._start_listening()
        elif new_state == VoiceTypingState.FINISH_LISTENING:
            self._stop_listening()
        elif new_state == VoiceTypingState.PROCESSING:
            self._process_audio()
        elif new_state == VoiceTypingState.IDLE:
            self._return_to_idle()
    
    def _start_listening(self):
        """Start audio capture for listening."""
        print("[System] Starting to listen...")
        
        def on_audio_chunk(chunk: bytes):
            # Process audio through recognition
            self.recognition_source.process_audio_chunk(chunk)
            
            # Check for results
            result = self.recognition_source.get_result()
            if result:
                print(f"[System] Recognition result: {result}")
                # Transition to processing state
                self.state_manager.set_state(VoiceTypingState.PROCESSING, {
                    'result': result
                })
        
        self.audio_input.start_capture(on_audio_chunk)
    
    def _stop_listening(self):
        """Stop audio capture."""
        print("[System] Stopping listening...")
        self.audio_input.stop_capture()
    
    def _process_audio(self):
        """Process recognized audio and deliver output."""
        print("[System] Processing recognition result...")
        
        # Get the result from state metadata
        metadata = self.state_manager.get_state_metadata()
        result = metadata.get('result', {})
        
        text = result.get('text', '')
        if text:
            # Deliver text through output target
            output_metadata = {
                'confidence': result.get('confidence', 0.0),
                'timestamp': time.time()
            }
            
            if self.output_target.deliver_text(text, output_metadata):
                print(f"[System] Successfully delivered text: '{text}'")
            else:
                print("[System] Failed to deliver text")
        
        # Return to idle after processing
        self.state_manager.set_state(VoiceTypingState.IDLE)
    
    def _return_to_idle(self):
        """Return system to idle state."""
        print("[System] Returning to idle state")
        # Ensure all capture is stopped
        if self.audio_input.is_capturing():
            self.audio_input.stop_capture()
    
    def start_voice_typing(self):
        """Start voice typing (simulate hotkey press)."""
        current_state = self.state_manager.get_current_state()
        
        if current_state == VoiceTypingState.IDLE:
            success = self.state_manager.set_state(VoiceTypingState.LISTENING, {
                'trigger': 'hotkey_press'
            })
            if success:
                print("[System] Voice typing started")
            else:
                print("[System] Failed to start voice typing")
    
    def stop_voice_typing(self):
        """Stop voice typing (simulate hotkey release)."""
        current_state = self.state_manager.get_current_state()
        
        if current_state == VoiceTypingState.LISTENING:
            success = self.state_manager.set_state(VoiceTypingState.FINISH_LISTENING, {
                'trigger': 'hotkey_release'
            })
            if success:
                print("[System] Voice typing stopped")
            else:
                print("[System] Failed to stop voice typing")
    
    def cleanup(self):
        """Clean up all subsystems."""
        print("[System] Cleaning up...")
        self.audio_input.cleanup()
        self.recognition_source.cleanup()
        self.output_target.cleanup()
        print("[System] Cleanup complete")


def demonstrate_integrated_system():
    """Demonstrate the complete integrated system."""
    print("=== Integrated Voice Typing System Demo ===\n")
    
    # Create all components
    audio_input = MockAudioInput()
    recognition_source = MockRecognitionSource()
    output_target = MockOutputTarget()
    state_manager = BasicStateManager()
    
    # Create integrated system
    system = IntegratedVoiceTypingSystem(
        audio_input, recognition_source, output_target, state_manager
    )
    
    # Initialize system
    if not system.initialize():
        print("Failed to initialize system")
        return
    
    print("\n--- Simulating Voice Typing Session ---")
    
    # Show initial state
    print(f"Initial state: {state_manager.get_current_state().value}")
    
    # Start voice typing
    print("\n1. User presses hotkey...")
    system.start_voice_typing()
    time.sleep(0.5)
    
    # Simulate audio input
    print("\n2. Simulating audio input...")
    if hasattr(audio_input, 'simulate_audio'):
        # Send some audio chunks to trigger recognition
        for i in range(4):  # MockRecognitionSource produces result after 3 chunks
            audio_input.simulate_audio(f"audio_chunk_{i}".encode())
            time.sleep(0.2)
    
    # Stop voice typing
    print("\n3. User releases hotkey...")
    system.stop_voice_typing()
    time.sleep(0.5)
    
    # Show final state
    print(f"\nFinal state: {state_manager.get_current_state().value}")
    
    # Show history
    print("\n--- State Transition History ---")
    history = state_manager.get_state_history()
    for transition in history:
        timestamp = time.strftime('%H:%M:%S', time.localtime(transition.timestamp))
        print(f"{timestamp}: {transition.from_state.value} → {transition.to_state.value}")
        if transition.metadata:
            print(f"  Metadata: {transition.metadata}")
    
    # Cleanup
    system.cleanup()
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demonstrate_integrated_system()