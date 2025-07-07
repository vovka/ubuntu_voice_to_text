"""
Keyboard Mode main file - Keyboard enabled, tray disabled.
Scenario 3: The Keyboard Listener unit waits for hotkeys, publishing events that other units
react to. The app idles until hotkeys trigger actions, and remains alive until explicitly exited.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dummy import *
from voice_typing.keyboard_listener.linux_keyboard_listener import LinuxKeyboardListener
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    Keyboard mode: Keyboard enabled, tray disabled. The app waits for hotkeys
    and triggers actions based on keyboard events.
    """
    logger.info("Starting Keyboard Mode (Keyboard Enabled, No Tray)")

    # Create shared queues for the pipeline
    hotkey_events_queue = (
        asyncio.Queue()
    )  # keyboard_listener -> sound_recorder, shared_state
    sound_control_queue = (
        asyncio.Queue()
    )  # receives control commands for sound_recorder
    audio_pipeline_queue = asyncio.Queue()  # sound_recorder -> noise_cancelling
    clean_audio_queue = asyncio.Queue()  # noise_cancelling -> voice_recognition
    recognized_text_queue = asyncio.Queue()  # voice_recognition -> output_handler

    # Create units for keyboard mode (no tray control)
    keyboard_listener = LinuxKeyboardListener(
        config={"hotkeys": ["ctrl+shift+r"]},
        output_queue=hotkey_events_queue,
        loop=asyncio.get_running_loop()
    )

    sound_recorder = DummySoundRecorder(
        config={"sample_rate": 44100},
        audio_output_queue=audio_pipeline_queue,
        control_queue=sound_control_queue,
    )

    noise_cancelling = DummyNoiseCancelling(
        config={"noise_level": 0.5},
        audio_input_queue=audio_pipeline_queue,
        audio_output_queue=clean_audio_queue,
    )

    voice_recognition = DummyVoiceRecognition(
        config={"engine": "vosk"},
        audio_input_queue=clean_audio_queue,
        text_output_queue=recognized_text_queue,
    )

    output_handler = DummyOutputHandler(
        config={"output_type": "clipboard"}, input_queue=recognized_text_queue
    )

    shared_state = DummySharedState()

    # Create a bridge task to handle hotkey events
    async def keyboard_event_bridge():
        """Bridge task to handle keyboard events and control the pipeline."""
        while True:
            try:
                hotkey_event = await hotkey_events_queue.get()
                logger.info(f"Keyboard mode: Received hotkey event '{hotkey_event}'")

                # Convert hotkey events to appropriate actions
                if "start_recording" in hotkey_event:
                    await sound_control_queue.put("start_recording")
                    await shared_state.state_queue.put("state_change:recording")
                    logger.info("Keyboard mode: Started recording via hotkey")

                elif "stop_recording" in hotkey_event:
                    await sound_control_queue.put("stop_recording")
                    await shared_state.state_queue.put("state_change:idle")
                    logger.info("Keyboard mode: Stopped recording via hotkey")

                # Also track hotkey events in shared state
                await shared_state.state_queue.put(f"hotkey_event:{hotkey_event}")

            except asyncio.CancelledError:
                logger.info("Keyboard mode: Event bridge stopped")
                break

    # Simulate exit hotkey handling
    async def exit_handler():
        """Handle exit condition - in real app this would be a specific hotkey."""
        await asyncio.sleep(12)  # Let the app run for a while
        logger.info("Keyboard mode: Simulating exit hotkey (Ctrl+Shift+Q)")
        await shared_state.state_queue.put("hotkey_event:exit")

    # Start all units
    units = [
        keyboard_listener,
        sound_recorder,
        noise_cancelling,
        voice_recognition,
        output_handler,
        shared_state,
    ]

    logger.info("Starting keyboard mode units...")
    tasks = [asyncio.create_task(unit.run()) for unit in units]
    bridge_task = asyncio.create_task(keyboard_event_bridge())
    exit_task = asyncio.create_task(exit_handler())

    # Let the system run (keyboard mode stays alive until explicitly exited)
    logger.info("Keyboard mode running - waiting for hotkeys...")
    await asyncio.sleep(15)

    # Clean shutdown
    logger.info("Keyboard mode shutting down...")

    # Stop all units
    for unit in units:
        if hasattr(unit, "stop"):
            unit.stop()

    # Cancel all tasks
    bridge_task.cancel()
    exit_task.cancel()
    for task in tasks:
        task.cancel()

    # Wait for all tasks to complete
    await asyncio.gather(bridge_task, exit_task, *tasks, return_exceptions=True)

    logger.info("Keyboard mode completed")


if __name__ == "__main__":
    asyncio.run(main())
