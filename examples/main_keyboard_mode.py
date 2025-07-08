"""
Keyboard Mode main file - Keyboard enabled, tray disabled.
Scenario 3: The Keyboard Listener unit waits for hotkeys, publishing events that other units
react to. The app idles until hotkeys trigger actions, and remains alive until explicitly exited.
"""

import sys
import os
import signal
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dummy import *
from voice_typing.keyboard_listener.linux_keyboard_listener import LinuxKeyboardListener
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    global shutdown_requested
    logger.info("Ctrl+C pressed - requesting shutdown...")
    shutdown_requested = True


async def main():
    """
    Keyboard mode: Keyboard enabled, tray disabled. The app waits for hotkeys
    and triggers actions based on keyboard events.
    """
    global shutdown_requested
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("Starting Keyboard Mode (Keyboard Enabled, No Tray)")
    logger.info("Press Ctrl+Shift+Alt+A to toggle recording, Ctrl+C to exit")

    # Create shared queues for the pipeline
    hotkey_events_queue = asyncio.Queue()  # keyboard_listener -> bridge
    sound_control_queue = asyncio.Queue()  # bridge -> sound_recorder
    audio_pipeline_queue = asyncio.Queue()  # sound_recorder -> noise_cancelling
    clean_audio_queue = asyncio.Queue()  # noise_cancelling -> voice_recognition
    recognized_text_queue = asyncio.Queue()  # voice_recognition -> output_handler
    tray_control_queue = asyncio.Queue()  # bridge -> tray_control
    shared_state_queue = asyncio.Queue()  # bridge -> shared_state

    # Create units for keyboard mode
    keyboard_listener = LinuxKeyboardListener(
        config={"hotkeys": ["ctrl+shift+alt+a"]},
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
        config={"output_type": "clipboard"}, 
        input_queue=recognized_text_queue
    )

    tray_control = DummyTrayControl(
        config={"enabled": False},
        input_queue=tray_control_queue
    )

    shared_state = DummySharedState()

    # Create a bridge task to handle keyboard events and orchestrate the pipeline
    async def keyboard_event_bridge():
        """Bridge task to handle keyboard events and control the pipeline."""
        recording_state = False
        
        while not shutdown_requested:
            try:
                hotkey_event = await asyncio.wait_for(hotkey_events_queue.get(), timeout=0.5)
                logger.info(f"Keyboard mode: Received hotkey event '{hotkey_event}'")

                # Toggle recording state
                if "start_recording" in hotkey_event or "stop_recording" in hotkey_event:
                    recording_state = not recording_state
                    
                    if recording_state:
                        # Start recording pipeline
                        await sound_control_queue.put("start_recording")
                        await tray_control_queue.put("state_change:recording")
                        await shared_state.state_queue.put("state_change:recording")
                        logger.info(">>> RECORDING STARTED - Pipeline active")
                    else:
                        # Stop recording pipeline
                        await sound_control_queue.put("stop_recording")
                        await tray_control_queue.put("state_change:idle")
                        await shared_state.state_queue.put("state_change:idle")
                        logger.info(">>> RECORDING STOPPED - Pipeline idle")

                # Track hotkey events in shared state
                await shared_state.state_queue.put(f"hotkey_event:{hotkey_event}")

            except asyncio.TimeoutError:
                # Check for shutdown periodically
                continue
            except asyncio.CancelledError:
                logger.info("Keyboard mode: Event bridge stopped")
                break

    # Start all units
    units = [
        keyboard_listener,
        sound_recorder,
        noise_cancelling,
        voice_recognition,
        output_handler,
        tray_control,
        shared_state,
    ]

    logger.info("Starting keyboard mode units...")
    tasks = [asyncio.create_task(unit.run()) for unit in units]
    bridge_task = asyncio.create_task(keyboard_event_bridge())

    try:
        # Let the system run until shutdown is requested
        logger.info("Keyboard mode running - waiting for hotkeys...")
        while not shutdown_requested:
            await asyncio.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
        shutdown_requested = True

    # Clean shutdown
    logger.info("Keyboard mode shutting down...")

    # Stop all units
    for unit in units:
        if hasattr(unit, "stop"):
            unit.stop()

    # Cancel all tasks
    bridge_task.cancel()
    for task in tasks:
        task.cancel()

    # Wait for all tasks to complete
    await asyncio.gather(bridge_task, *tasks, return_exceptions=True)

    logger.info("Keyboard mode completed")


if __name__ == "__main__":
    asyncio.run(main())
