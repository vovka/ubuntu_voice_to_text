"""
Full Mode main file - Both tray and keyboard enabled.
Scenario 4: The Tray Control unit reflects state changes, and the Keyboard Listener unit
publishes events, with other units reacting to these events to manage recording, transcription,
and output. Exiting is typically via the tray menu.
"""

from dummy import *
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    Full mode: Both tray and keyboard enabled. The system provides maximum
    control and feedback through both keyboard shortcuts and tray interaction.
    """
    logger.info("Starting Full Mode (Tray + Keyboard)")

    # Create shared queues for the complete pipeline
    hotkey_events_queue = (
        asyncio.Queue()
    )  # keyboard_listener -> sound_recorder, shared_state
    sound_control_queue = (
        asyncio.Queue()
    )  # receives control commands for sound_recorder
    audio_pipeline_queue = asyncio.Queue()  # sound_recorder -> noise_cancelling
    clean_audio_queue = asyncio.Queue()  # noise_cancelling -> voice_recognition
    recognized_text_queue = asyncio.Queue()  # voice_recognition -> output_handler
    state_updates_queue = asyncio.Queue()  # shared_state -> tray_control

    # Create all units for full mode
    keyboard_listener = DummyKeyboardListener(
        config={"hotkeys": ["ctrl+shift+r", "ctrl+shift+q"]},
        output_queue=hotkey_events_queue,
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

    shared_state = DummySharedState(state_queue=state_updates_queue)

    tray_control = DummyTrayControl(
        config={"tray_style": "gnome"}, input_queue=state_updates_queue
    )

    # Create a comprehensive bridge for full mode
    async def full_mode_bridge():
        """Bridge task for full mode - handles keyboard events and coordinates state."""
        while True:
            try:
                hotkey_event = await hotkey_events_queue.get()
                logger.info(f"Full mode: Received hotkey event '{hotkey_event}'")

                # Handle recording control
                if "start_recording" in hotkey_event:
                    await sound_control_queue.put("start_recording")
                    await state_updates_queue.put("state_change:listening")
                    logger.info("Full mode: Started recording via hotkey, tray updated")

                elif "stop_recording" in hotkey_event:
                    await sound_control_queue.put("stop_recording")
                    await state_updates_queue.put("state_change:idle")
                    logger.info("Full mode: Stopped recording via hotkey, tray updated")

                # Handle exit command
                elif "exit" in hotkey_event or "quit" in hotkey_event:
                    await state_updates_queue.put("tray_event:exit")
                    logger.info("Full mode: Exit requested via hotkey")
                    break

                # Forward all hotkey events to shared state
                await state_updates_queue.put(f"hotkey_event:{hotkey_event}")

            except asyncio.CancelledError:
                logger.info("Full mode: Bridge stopped")
                break

    # Simulate tray interactions in full mode
    async def tray_interaction_simulator():
        """Simulate tray menu interactions in full mode."""
        await asyncio.sleep(8)  # Let keyboard interactions happen first

        # Simulate tray menu actions
        await state_updates_queue.put("tray_event:show_about")
        logger.info("Full mode: Simulated tray 'About' action")

        await asyncio.sleep(2)
        await state_updates_queue.put("tray_event:show_settings")
        logger.info("Full mode: Simulated tray 'Settings' action")

        await asyncio.sleep(3)
        await state_updates_queue.put("tray_event:exit")
        logger.info("Full mode: Simulated tray 'Exit' action")

    # Start all units
    units = [
        keyboard_listener,
        sound_recorder,
        noise_cancelling,
        voice_recognition,
        output_handler,
        shared_state,
        tray_control,
    ]

    logger.info("Starting full mode units...")
    tasks = [asyncio.create_task(unit.run()) for unit in units]
    bridge_task = asyncio.create_task(full_mode_bridge())
    tray_simulator_task = asyncio.create_task(tray_interaction_simulator())

    # Let the system run (full mode provides maximum functionality)
    logger.info("Full mode running - keyboard shortcuts and tray both active...")
    await asyncio.sleep(15)

    # Clean shutdown
    logger.info("Full mode shutting down...")

    # Stop all units
    for unit in units:
        if hasattr(unit, "stop"):
            unit.stop()

    # Cancel all tasks
    bridge_task.cancel()
    tray_simulator_task.cancel()
    for task in tasks:
        task.cancel()

    # Wait for all tasks to complete
    await asyncio.gather(
        bridge_task, tray_simulator_task, *tasks, return_exceptions=True
    )

    logger.info("Full mode completed")


if __name__ == "__main__":
    asyncio.run(main())
