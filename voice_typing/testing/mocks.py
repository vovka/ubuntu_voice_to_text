"""
Centralized mock implementations for all voice typing system interfaces.

This module provides reusable mock classes that implement all the main interfaces,
designed for use in unit tests and examples.
"""

from typing import Dict, Any, Optional, Callable, List
from ..interfaces import (
    AudioInputSource,
    VoiceRecognitionSource,
    OutputActionTarget,
    OutputType,
    StateManager,
    VoiceTypingState,
    StateTransition,
)


class MockAudioInputSource(AudioInputSource):
    """Mock implementation of AudioInputSource for testing."""
    
    def __init__(self):
        self._initialized = False
        self._capturing = False
        self._callback: Optional[Callable[[bytes], None]] = None
        self._simulate_audio_data = []

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the mock audio input."""
        self._initialized = True
        return True

    def start_capture(self, callback: Callable[[bytes], None]) -> bool:
        """Start capturing audio."""
        if not self._initialized:
            return False
        self._callback = callback
        self._capturing = True
        return True

    def stop_capture(self) -> None:
        """Stop capturing audio."""
        self._capturing = False
        self._callback = None

    def is_capturing(self) -> bool:
        """Check if currently capturing."""
        return self._capturing

    def is_available(self) -> bool:
        """Check if audio input is available."""
        return True

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop_capture()
        self._initialized = False

    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """Get device information."""
        return {'name': 'Mock Device', 'channels': 1, 'sample_rate': 16000}

    def simulate_audio_chunk(self, audio_data: bytes) -> None:
        """Simulate receiving audio data (test helper method)."""
        if self._callback and self._capturing:
            self._callback(audio_data)


class MockVoiceRecognitionSource(VoiceRecognitionSource):
    """Mock implementation of VoiceRecognitionSource for testing."""
    
    def __init__(self):
        self._initialized = False
        self._chunks = []
        self._results = []
        self._recognition_results = [
            {'text': 'hello world', 'confidence': 0.95, 'final': True},
            {'text': 'test recognition', 'confidence': 0.90, 'final': True},
            {'text': 'mock result', 'confidence': 0.85, 'final': True},
        ]
        self._result_index = 0

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the mock recognition source."""
        self._initialized = True
        return True

    def process_audio_chunk(self, audio_chunk: bytes) -> None:
        """Process an audio chunk."""
        if self._initialized:
            self._chunks.append(audio_chunk)
            # Simulate recognition result after processing a few chunks
            if len(self._chunks) >= 3:
                result = self._recognition_results[self._result_index % len(self._recognition_results)]
                self._results.append(result.copy())
                self._result_index += 1
                self._chunks.clear()  # Reset chunks after generating result

    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get the next available recognition result."""
        return self._results.pop(0) if self._results else None

    def is_available(self) -> bool:
        """Check if recognition source is available."""
        return self._initialized

    def cleanup(self) -> None:
        """Clean up resources."""
        self._chunks.clear()
        self._results.clear()
        self._initialized = False

    def set_recognition_results(self, results: List[Dict[str, Any]]) -> None:
        """Set custom recognition results for testing."""
        self._recognition_results = results
        self._result_index = 0

    def add_pending_result(self, result: Dict[str, Any]) -> None:
        """Add a result to the pending results queue."""
        self._results.append(result)


class MockOutputActionTarget(OutputActionTarget):
    """Mock implementation of OutputActionTarget for testing."""
    
    def __init__(self, output_type: OutputType = OutputType.CALLBACK):
        self._initialized = False
        self._delivered_texts = []
        self._output_type = output_type
        self._supports_formatting = False

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the mock output target."""
        self._initialized = True
        return True

    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Deliver text to the mock target."""
        if not self._initialized:
            return False
        self._delivered_texts.append((text, metadata or {}))
        return True

    def is_available(self) -> bool:
        """Check if output target is available."""
        return self._initialized

    def get_output_type(self) -> OutputType:
        """Get the output type."""
        return self._output_type

    def supports_formatting(self) -> bool:
        """Check if formatting is supported."""
        return self._supports_formatting

    def cleanup(self) -> None:
        """Clean up resources."""
        self._delivered_texts.clear()
        self._initialized = False

    def get_delivered_texts(self) -> List[tuple]:
        """Get all delivered texts (test helper method)."""
        return self._delivered_texts.copy()

    def clear_delivered_texts(self) -> None:
        """Clear delivered texts (test helper method)."""
        self._delivered_texts.clear()

    def set_supports_formatting(self, supports: bool) -> None:
        """Set formatting support flag (test helper method)."""
        self._supports_formatting = supports


class MockStateManager(StateManager):
    """Mock implementation of StateManager for testing."""
    
    def __init__(self):
        self._current_state = VoiceTypingState.IDLE
        self._state_history = []
        self._listeners = []
        self._metadata = {}

    def get_current_state(self) -> VoiceTypingState:
        """Get the current state."""
        return self._current_state

    def set_state(self, new_state: VoiceTypingState, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Set a new state."""
        if not self.can_transition_to(new_state):
            return False
        
        old_state = self._current_state
        self._current_state = new_state
        self._metadata = metadata or {}
        
        # Create transition record
        transition = StateTransition(old_state, new_state, metadata)
        self._state_history.append(transition)
        
        # Notify listeners
        for listener in self._listeners:
            try:
                listener(transition)
            except Exception:
                # Ignore listener errors in mock
                pass
        
        return True

    def can_transition_to(self, new_state: VoiceTypingState) -> bool:
        """Check if transition to new state is allowed."""
        # Allow all transitions in mock for testing flexibility
        return True

    def register_state_listener(self, listener: Callable[[StateTransition], None]) -> None:
        """Register a state change listener."""
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unregister_state_listener(self, listener: Callable[[StateTransition], None]) -> None:
        """Unregister a state change listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def get_state_history(self, limit: Optional[int] = None) -> List[StateTransition]:
        """Get state transition history."""
        history = self._state_history.copy()
        if limit is not None:
            history = history[-limit:]
        return history

    def get_state_metadata(self) -> Dict[str, Any]:
        """Get metadata for current state."""
        return self._metadata.copy()

    def reset_state(self) -> None:
        """Reset to initial state."""
        self._current_state = VoiceTypingState.IDLE
        self._state_history.clear()
        self._metadata.clear()

    def clear_listeners(self) -> None:
        """Clear all listeners (test helper method)."""
        self._listeners.clear()

    def get_listener_count(self) -> int:
        """Get number of registered listeners (test helper method)."""
        return len(self._listeners)