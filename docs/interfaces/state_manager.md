# State Manager Interface

The State Manager Interface defines how application state transitions are managed and how subsystems can be notified of state changes through event hooks.

## Interface Contract

### StateManager (Abstract Base Class)

```python
from voice_typing.interfaces import StateManager, VoiceTypingState, StateTransition

class MyStateManager(StateManager):
    def get_current_state(self) -> VoiceTypingState:
        # Return current application state
        pass
    
    def set_state(self, new_state: VoiceTypingState, metadata: Optional[Dict[str, Any]] = None) -> bool:
        # Change to new state with optional metadata
        pass
    
    def can_transition_to(self, new_state: VoiceTypingState) -> bool:
        # Check if transition to new state is allowed
        pass
    
    def register_state_listener(self, listener: Callable[[StateTransition], None]) -> None:
        # Register callback for state changes
        pass
    
    def unregister_state_listener(self, listener: Callable[[StateTransition], None]) -> None:
        # Remove state change callback
        pass
    
    def get_state_history(self, limit: Optional[int] = None) -> list[StateTransition]:
        # Get recent state transitions
        pass
    
    def get_state_metadata(self) -> Dict[str, Any]:
        # Get metadata for current state
        pass
    
    def reset_state(self) -> None:
        # Reset to initial state
        pass
```

## Voice Typing States

The system uses the `VoiceTypingState` enum to define valid states:

- `IDLE` - System is idle, not listening
- `LISTENING` - Actively capturing audio input
- `FINISH_LISTENING` - Finished capturing, preparing to process
- `PROCESSING` - Recognition processing in progress
- `ERROR` - Error condition requiring attention

## State Transitions

Valid state transitions are enforced by the state manager:

```
IDLE → LISTENING, ERROR
LISTENING → FINISH_LISTENING, IDLE, ERROR  
FINISH_LISTENING → PROCESSING, IDLE, ERROR
PROCESSING → IDLE, ERROR
ERROR → IDLE
```

## Usage Examples

### Basic State Manager Implementation

```python
from voice_typing.interfaces import BasicStateManager, VoiceTypingState

# Create state manager
state_manager = BasicStateManager()

# Check current state
current = state_manager.get_current_state()
print(f"Current state: {current}")  # IDLE

# Change state
if state_manager.can_transition_to(VoiceTypingState.LISTENING):
    success = state_manager.set_state(VoiceTypingState.LISTENING)
    print(f"State change successful: {success}")
```

### State Change Listeners

```python
def on_state_change(transition: StateTransition):
    print(f"State changed: {transition.from_state} → {transition.to_state}")
    print(f"Timestamp: {transition.timestamp}")
    if transition.metadata:
        print(f"Metadata: {transition.metadata}")

# Register listener
state_manager.register_state_listener(on_state_change)

# Change state (listener will be called)
state_manager.set_state(VoiceTypingState.LISTENING, 
                       {'trigger': 'hotkey_pressed'})
```

### State History Tracking

```python
# Get recent state transitions
history = state_manager.get_state_history(limit=5)
for transition in history:
    print(f"{transition.from_state} → {transition.to_state} at {transition.timestamp}")

# Get all history
all_history = state_manager.get_state_history()
```

### Using with Legacy GlobalState

For backward compatibility, use `LegacyStateManagerAdapter`:

```python
from voice_typing.interfaces.state_manager import LegacyStateManagerAdapter
from voice_typing import GlobalState

# Wrap existing GlobalState
global_state = GlobalState()
state_manager = LegacyStateManagerAdapter(global_state)

# Now you can use the new interface
state_manager.register_state_listener(my_listener)
state_manager.set_state(VoiceTypingState.LISTENING)
```

## Advanced Usage

### Custom State Manager with Validation

```python
class ValidatingStateManager(BasicStateManager):
    def set_state(self, new_state: VoiceTypingState, metadata: Optional[Dict[str, Any]] = None) -> bool:
        # Custom validation logic
        if new_state == VoiceTypingState.LISTENING:
            # Check if audio input is available
            if not self._audio_available():
                print("Cannot start listening: no audio input available")
                return False
        
        # Call parent implementation
        return super().set_state(new_state, metadata)
    
    def _audio_available(self) -> bool:
        # Check audio availability
        try:
            import sounddevice as sd
            return len(sd.query_devices(kind='input')) > 0
        except:
            return False
```

### State-Based Component Coordination

```python
class VoiceTypingCoordinator:
    def __init__(self, state_manager: StateManager, audio_processor, ui_manager):
        self.state_manager = state_manager
        self.audio_processor = audio_processor
        self.ui_manager = ui_manager
        
        # Register for state changes
        state_manager.register_state_listener(self._on_state_change)
    
    def _on_state_change(self, transition: StateTransition):
        """Coordinate components based on state changes."""
        new_state = transition.to_state
        
        if new_state == VoiceTypingState.LISTENING:
            self.audio_processor.start_listening()
            self.ui_manager.show_listening_indicator()
            
        elif new_state == VoiceTypingState.IDLE:
            self.audio_processor.stop_listening()
            self.ui_manager.hide_listening_indicator()
            
        elif new_state == VoiceTypingState.ERROR:
            self.ui_manager.show_error_message(transition.metadata.get('error'))
```

## StateTransition Object

The `StateTransition` object provides details about state changes:

```python
class StateTransition:
    from_state: VoiceTypingState    # Previous state
    to_state: VoiceTypingState      # New state
    metadata: Dict[str, Any]        # Optional metadata
    timestamp: float                # When transition occurred
```

## Metadata Examples

State transitions can include metadata for additional context:

```python
# Starting to listen due to hotkey
state_manager.set_state(VoiceTypingState.LISTENING, {
    'trigger': 'hotkey',
    'hotkey_combo': 'Ctrl+Shift'
})

# Error with details
state_manager.set_state(VoiceTypingState.ERROR, {
    'error_type': 'audio_device_error',
    'error_message': 'Microphone not found',
    'recovery_action': 'check_audio_settings'
})

# Processing with progress info
state_manager.set_state(VoiceTypingState.PROCESSING, {
    'audio_duration': 2.5,
    'recognition_engine': 'whisper'
})
```

## Thread Safety

State managers should be thread-safe when used across multiple threads:

```python
import threading

class ThreadSafeStateManager(BasicStateManager):
    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()
    
    def set_state(self, new_state: VoiceTypingState, metadata: Optional[Dict[str, Any]] = None) -> bool:
        with self._lock:
            return super().set_state(new_state, metadata)
    
    def get_current_state(self) -> VoiceTypingState:
        with self._lock:
            return super().get_current_state()
```

## Error Handling

- Return `False` from `set_state()` if transition is not allowed
- Handle exceptions in state listeners gracefully
- Log state transition errors for debugging
- Provide recovery mechanisms for error states
- Ensure state consistency even if listeners fail