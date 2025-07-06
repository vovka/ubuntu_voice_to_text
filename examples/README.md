# Examples

This directory contains example files demonstrating how to use the Ubuntu Voice-to-Text application in different modes.

## Main Application Examples

### `main.py`
Main demo that shows all units working together with inter-unit communication via shared queues.

### `main_bare_mode.py`
**Bare Mode** - No tray, no keyboard. The app starts, processes audio automatically, and exits.

### `main_keyboard_mode.py`
**Keyboard Mode** - Keyboard enabled, tray disabled. The app waits for hotkeys and triggers actions based on keyboard events.

### `main_full_mode.py`
**Full Mode** - Both tray and keyboard enabled. Maximum control and feedback through both keyboard shortcuts and tray interaction.

### `main_tray_mode.py`
**Tray Mode** - Tray enabled, keyboard disabled. The tray icon reflects state changes and provides user interaction.

## Simple Examples

### `bare_keyboard_example.py`
A minimal keyboard listener example that demonstrates:
- Basic hotkey detection (Ctrl+Shift+Alt+A)
- Toggle functionality (outputs "on" then "off")
- Graceful exit with Ctrl+C

This is the simplest way to understand how the keyboard listener works.

## Running Examples

All examples can be run from the project root directory:

```bash
# Run bare keyboard example
python examples/bare_keyboard_example.py

# Run application modes
python examples/main_bare_mode.py
python examples/main_keyboard_mode.py
python examples/main_full_mode.py
python examples/main_tray_mode.py
python examples/main.py
```

## Environment Notes

- In environments without X server (like CI), the keyboard listener will fall back to dummy mode
- The bare keyboard example is designed to work in both real and fallback environments
- All examples handle graceful shutdown and proper cleanup