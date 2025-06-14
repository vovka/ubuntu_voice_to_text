# TrayIconManager UI Event Subscriptions

## Overview

The TrayIconManager has been refactored to be a pure UI subscriber that only reacts to explicit state changes through event subscriptions. This document outlines the event subscriptions and interactions for the UI layer.

## Event Subscription Architecture

### StateManager Integration

The TrayIconManager subscribes to state changes through the `StateManager` interface:

```python
# During initialization
if self.state_manager:
    self.state_manager.register_state_listener(self._on_state_change)
```

### Core Event Handler

The primary event handler that responds to all state transitions:

```python
def _on_state_change(self, transition: StateTransition) -> None:
    """
    React to state changes by updating the tray icon.
    
    This is the core event subscription that makes TrayIconManager
    a pure subscriber to state changes.
    """
```

## UI Event Interactions

### State Change Events

The TrayIconManager responds to the following state transition events:

| From State | To State | UI Response |
|------------|----------|-------------|
| Any | `IDLE` | Gray icon, "Voice Typing: OFF" title |
| Any | `LISTENING` | Green icon, "Voice Typing: ON" title |
| Any | `FINISH_LISTENING` | Blue icon, "Voice Typing: finish_listening" title |
| Any | `PROCESSING` | Gray icon, "Voice Typing: OFF" title |
| Any | `ERROR` | Gray icon, "Voice Typing: OFF" title |

### Event Metadata

State transitions can include metadata that provides additional context:

```python
# Example: State change triggered by hotkey
state_manager.set_state(VoiceTypingState.LISTENING, {
    'trigger': 'hotkey',
    'hotkey_combo': 'Ctrl+Shift'
})
```

### Icon Visual Mapping

The UI provides visual feedback based on state:

- **IDLE/PROCESSING/ERROR**: Gray circle (120, 120, 120)
- **LISTENING**: Green circle (40, 255, 40) 
- **FINISH_LISTENING**: Blue circle (40, 150, 150)

## Decoupling Principles

### Pure UI Subscriber

The TrayIconManager follows these principles:

1. **No Direct State Access**: Does not read state directly from GlobalState
2. **No State Mutation**: Does not modify application state
3. **Event-Driven Updates**: Only updates UI in response to state change events
4. **Business Logic Separation**: Delegates business logic (like exit) through callbacks

### Backward Compatibility

For gradual migration, the TrayIconManager supports both:

- **New Event-Driven Mode**: When `state_manager` is provided
- **Legacy Mode**: When only `state_ref` is provided (deprecated)

```python
# New approach (recommended)
tray_icon_manager = TrayIconManager(
    state_manager=state_manager,
    exit_callback=handle_exit
)

# Legacy approach (deprecated)
tray_icon_manager = TrayIconManager(state_ref=state_ref)
```

## Exit Event Handling

The UI layer delegates exit requests through callbacks to avoid business logic:

```python
def exit_application(self, icon, item):
    """Handle exit request from tray menu."""
    icon.stop()  # UI cleanup
    if self.exit_callback:
        self.exit_callback()  # Delegate business logic
```

## Migration Guide

### For New Code

Use the StateManager-based approach:

```python
def handle_app_exit():
    # Business logic for clean exit
    cleanup_resources()
    os._exit(0)

tray_icon_manager = TrayIconManager(
    state_manager=state_manager,
    exit_callback=handle_app_exit
)

# No need to call update_icon() - happens automatically via events
```

### For Existing Code

The legacy interface remains functional:

```python
# Old code continues to work
tray_icon_manager = TrayIconManager(state_ref)
tray_icon_manager.update_icon()  # Shows deprecation warning
```

## Event Flow Diagram

```
StateManager → StateTransition Event → TrayIconManager._on_state_change()
                                     ↓
                              _update_icon_for_state()
                                     ↓
                              Visual Icon Update
```

## Benefits of Event-Driven Architecture

1. **Loose Coupling**: UI layer doesn't depend on specific state implementation
2. **Testability**: Easy to test by triggering state events
3. **Maintainability**: Clear separation of concerns
4. **Extensibility**: Easy to add new UI reactions to state changes
5. **Thread Safety**: State changes handled through centralized event system

## Testing

The decoupled architecture enables focused testing:

```python
# Test state event subscription
state_manager = BasicStateManager()
tray_icon_manager = TrayIconManager(state_manager=state_manager)
assert len(state_manager._listeners) == 1

# Test UI reaction to events
state_manager.set_state(VoiceTypingState.LISTENING)
assert tray_icon_manager._current_state == VoiceTypingState.LISTENING
```