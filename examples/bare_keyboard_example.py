#!/usr/bin/env python3
"""
Bare Keyboard Example - Minimal keyboard listener demonstration.

This example shows how to use the LinuxKeyboardListener in its simplest form.
It waits for the Ctrl+Shift+Alt+A hotkey and toggles between "on" and "off" states,
outputting the current state to the console. Press Ctrl+C to exit.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
import signal
from voice_typing.keyboard_listener.linux_keyboard_listener import LinuxKeyboardListener

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ToggleState:
    """Simple state tracker for on/off toggle."""
    
    def __init__(self):
        self.is_on = False
    
    def toggle(self):
        """Toggle the state and return the new state."""
        self.is_on = not self.is_on
        return "on" if self.is_on else "off"


async def main():
    """
    Main function that demonstrates bare keyboard listening.
    """
    print("Bare Keyboard Example")
    print("====================")
    print("Press Ctrl+Shift+Alt+A to toggle state")
    print("Press Ctrl+C to exit")
    print()
    
    # Create toggle state tracker
    toggle_state = ToggleState()
    
    # Create queue for keyboard events
    keyboard_events_queue = asyncio.Queue()
    
    # Create keyboard listener
    keyboard_listener = LinuxKeyboardListener(
        config={"hotkeys": ["ctrl+shift+alt+a"]},
        output_queue=keyboard_events_queue,
        loop=asyncio.get_running_loop()
    )
    
    # Flag to control the main loop
    running = True
    
    def signal_handler(signum, frame):
        """Handle Ctrl+C gracefully."""
        nonlocal running
        logger.info("Received signal %d, shutting down...", signum)
        running = False
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Event handler task
    async def handle_keyboard_events():
        """Handle keyboard events from the listener."""
        while running:
            try:
                # Wait for keyboard events with timeout to check running flag
                event = await asyncio.wait_for(keyboard_events_queue.get(), timeout=0.1)
                
                logger.info(f"Received keyboard event: {event}")
                
                # Toggle state on any hotkey event
                if "ctrl+shift" in event:
                    new_state = toggle_state.toggle()
                    print(f"State: {new_state}")
                    
            except asyncio.TimeoutError:
                # Continue checking running flag
                continue
            except asyncio.CancelledError:
                logger.info("Event handler cancelled")
                break
    
    # Start tasks
    logger.info("Starting bare keyboard listener...")
    
    # Start the keyboard listener
    listener_task = asyncio.create_task(keyboard_listener.run())
    
    # Start event handler
    event_handler_task = asyncio.create_task(handle_keyboard_events())
    
    # Wait for interruption
    try:
        while running:
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        running = False
    
    # Clean shutdown
    logger.info("Shutting down...")
    
    # Stop the keyboard listener
    keyboard_listener.stop()
    
    # Cancel tasks
    listener_task.cancel()
    event_handler_task.cancel()
    
    # Wait for tasks to complete
    await asyncio.gather(listener_task, event_handler_task, return_exceptions=True)
    
    print("Bare keyboard example completed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")