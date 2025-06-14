"""
Example implementation and usage of StateManager interface.

This demonstrates how to use the StateManager interface for 
coordinating application state and handling state transitions.
"""

import time
from typing import Dict, Any
from voice_typing.interfaces import StateManager, VoiceTypingState, StateTransition
from voice_typing.interfaces.state_manager import BasicStateManager


class VoiceTypingCoordinator:
    """
    Example coordinator that uses StateManager to orchestrate different components.
    
    This shows how the StateManager interface can be used to coordinate
    multiple subsystems in response to state changes.
    """

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.audio_active = False
        self.ui_listening_indicator = False
        
        # Register for state change notifications
        self.state_manager.register_state_listener(self._on_state_change)
        print("[Coordinator] Initialized and registered for state changes")

    def _on_state_change(self, transition: StateTransition):
        """Handle state changes by coordinating subsystems."""
        print(f"[Coordinator] State transition: {transition.from_state.value} -> {transition.to_state.value}")
        
        if transition.metadata:
            print(f"[Coordinator] Transition metadata: {transition.metadata}")
        
        # Coordinate based on new state
        new_state = transition.to_state
        
        if new_state == VoiceTypingState.LISTENING:
            self._start_listening()
            
        elif new_state == VoiceTypingState.FINISH_LISTENING:
            self._prepare_processing()
            
        elif new_state == VoiceTypingState.PROCESSING:
            self._start_processing()
            
        elif new_state == VoiceTypingState.IDLE:
            self._stop_all_activities()
            
        elif new_state == VoiceTypingState.ERROR:
            self._handle_error(transition.metadata)

    def _start_listening(self):
        """Start audio capture and show listening UI."""
        print("[Coordinator] Starting audio capture...")
        self.audio_active = True
        self.ui_listening_indicator = True
        print("[Coordinator] 🎤 Listening indicator ON")

    def _prepare_processing(self):
        """Prepare for processing captured audio."""
        print("[Coordinator] Preparing to process audio...")
        self.audio_active = False  # Stop capturing new audio
        print("[Coordinator] 🔄 Processing indicator ON")

    def _start_processing(self):
        """Start recognition processing."""
        print("[Coordinator] Starting recognition processing...")
        # In real implementation, this would start the recognition engine

    def _stop_all_activities(self):
        """Stop all activities and return to idle."""
        print("[Coordinator] Stopping all activities...")
        self.audio_active = False
        self.ui_listening_indicator = False
        print("[Coordinator] 💤 All indicators OFF")

    def _handle_error(self, metadata: Dict[str, Any]):
        """Handle error states."""
        error_type = metadata.get('error_type', 'unknown') if metadata else 'unknown'
        error_message = metadata.get('error_message', 'No details') if metadata else 'No details'
        
        print(f"[Coordinator] ❌ Error: {error_type} - {error_message}")
        
        # Stop all activities on error
        self.audio_active = False
        self.ui_listening_indicator = False

    def trigger_hotkey_press(self):
        """Simulate hotkey press to start listening."""
        current_state = self.state_manager.get_current_state()
        
        if current_state == VoiceTypingState.IDLE:
            metadata = {
                'trigger': 'hotkey',
                'hotkey_combo': 'Ctrl+Shift'
            }
            success = self.state_manager.set_state(VoiceTypingState.LISTENING, metadata)
            if success:
                print("[Coordinator] Hotkey triggered listening")
            else:
                print("[Coordinator] Failed to start listening")
        else:
            print(f"[Coordinator] Cannot start listening from state: {current_state.value}")

    def trigger_hotkey_release(self):
        """Simulate hotkey release to stop listening."""
        current_state = self.state_manager.get_current_state()
        
        if current_state == VoiceTypingState.LISTENING:
            metadata = {'trigger': 'hotkey_release'}
            success = self.state_manager.set_state(VoiceTypingState.FINISH_LISTENING, metadata)
            if success:
                print("[Coordinator] Hotkey release triggered processing")
            else:
                print("[Coordinator] Failed to stop listening")
        else:
            print(f"[Coordinator] Cannot stop listening from state: {current_state.value}")

    def simulate_recognition_complete(self, text: str, confidence: float):
        """Simulate completion of recognition processing."""
        current_state = self.state_manager.get_current_state()
        
        if current_state == VoiceTypingState.PROCESSING:
            metadata = {
                'recognized_text': text,
                'confidence': confidence,
                'duration': 1.5
            }
            print(f"[Coordinator] Recognition complete: '{text}' (confidence: {confidence})")
            
            # Return to idle after successful recognition
            success = self.state_manager.set_state(VoiceTypingState.IDLE, metadata)
            if not success:
                print("[Coordinator] Failed to return to idle")

    def simulate_error(self, error_type: str, error_message: str):
        """Simulate an error condition."""
        metadata = {
            'error_type': error_type,
            'error_message': error_message,
            'recovery_action': 'restart_audio'
        }
        success = self.state_manager.set_state(VoiceTypingState.ERROR, metadata)
        if success:
            print(f"[Coordinator] Error state set: {error_type}")
        else:
            print("[Coordinator] Failed to set error state")

    def recover_from_error(self):
        """Recover from error state."""
        current_state = self.state_manager.get_current_state()
        
        if current_state == VoiceTypingState.ERROR:
            success = self.state_manager.set_state(VoiceTypingState.IDLE)
            if success:
                print("[Coordinator] Recovered from error, back to idle")
            else:
                print("[Coordinator] Failed to recover from error")

    def show_status(self):
        """Show current system status."""
        current_state = self.state_manager.get_current_state()
        metadata = self.state_manager.get_state_metadata()
        
        print(f"\n[Coordinator] === Status ===")
        print(f"Current State: {current_state.value}")
        print(f"Audio Active: {self.audio_active}")
        print(f"UI Listening: {self.ui_listening_indicator}")
        if metadata:
            print(f"State Metadata: {metadata}")
        print("[Coordinator] ===============")

    def show_history(self, limit: int = 5):
        """Show recent state transition history."""
        history = self.state_manager.get_state_history(limit)
        
        print(f"\n[Coordinator] === Recent Transitions (last {limit}) ===")
        for transition in history[-limit:]:
            timestamp = time.strftime('%H:%M:%S', time.localtime(transition.timestamp))
            print(f"{timestamp}: {transition.from_state.value} -> {transition.to_state.value}")
            if transition.metadata:
                print(f"  Metadata: {transition.metadata}")
        print("[Coordinator] ========================================")


def demonstrate_basic_usage():
    """Demonstrate basic StateManager usage."""
    print("=== Basic StateManager Usage ===")
    
    # Create state manager
    state_manager = BasicStateManager()
    
    # Show initial state
    print(f"Initial state: {state_manager.get_current_state().value}")
    
    # Try some state transitions
    print("\nTesting valid transitions:")
    
    # IDLE -> LISTENING
    success = state_manager.set_state(VoiceTypingState.LISTENING, {'trigger': 'test'})
    print(f"IDLE -> LISTENING: {success}")
    
    # LISTENING -> FINISH_LISTENING
    success = state_manager.set_state(VoiceTypingState.FINISH_LISTENING)
    print(f"LISTENING -> FINISH_LISTENING: {success}")
    
    # FINISH_LISTENING -> PROCESSING
    success = state_manager.set_state(VoiceTypingState.PROCESSING)
    print(f"FINISH_LISTENING -> PROCESSING: {success}")
    
    # PROCESSING -> IDLE
    success = state_manager.set_state(VoiceTypingState.IDLE)
    print(f"PROCESSING -> IDLE: {success}")
    
    print("\nTesting invalid transition:")
    # IDLE -> PROCESSING (should fail)
    success = state_manager.set_state(VoiceTypingState.PROCESSING)
    print(f"IDLE -> PROCESSING: {success}")


def demonstrate_coordination():
    """Demonstrate coordinated system using StateManager."""
    print("\n=== Coordinated System Demo ===")
    
    # Create state manager and coordinator
    state_manager = BasicStateManager()
    coordinator = VoiceTypingCoordinator(state_manager)
    
    coordinator.show_status()
    
    # Simulate user interaction flow
    print("\n1. User presses hotkey to start listening...")
    coordinator.trigger_hotkey_press()
    coordinator.show_status()
    
    time.sleep(1)
    
    print("\n2. User releases hotkey to stop listening...")
    coordinator.trigger_hotkey_release()
    coordinator.show_status()
    
    # Transition to processing
    state_manager.set_state(VoiceTypingState.PROCESSING)
    
    time.sleep(1)
    
    print("\n3. Recognition completes successfully...")
    coordinator.simulate_recognition_complete("hello world", 0.95)
    coordinator.show_status()
    
    time.sleep(1)
    
    print("\n4. Simulate an error...")
    coordinator.simulate_error("audio_device_error", "Microphone disconnected")
    coordinator.show_status()
    
    time.sleep(1)
    
    print("\n5. Recover from error...")
    coordinator.recover_from_error()
    coordinator.show_status()
    
    # Show history
    coordinator.show_history()


if __name__ == "__main__":
    # Run demonstrations
    demonstrate_basic_usage()
    demonstrate_coordination()
    
    print("\nStateManager interface example completed!")