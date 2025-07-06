"""
Tray Mode main file - Tray enabled, keyboard disabled.
Scenario 2: The tray icon reflects the app's state, updated by messages from the Shared State unit.
Otherwise, it operates similarly to bare mode, with units reacting to events.
"""

from dummy import *
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    Tray mode: Tray enabled, keyboard disabled. The tray icon reflects state changes
    and the system operates with internal event reactions.
    """
    logger.info("Starting Tray Mode (Tray Enabled, No Keyboard)")

    # Create shared queues for the audio pipeline and state management
    audio_pipeline_queue = asyncio.Queue()  # sound_recorder -> noise_cancelling
    clean_audio_queue = asyncio.Queue()  # noise_cancelling -> voice_recognition
    recognized_text_queue = asyncio.Queue()  # voice_recognition -> output_handler
    state_updates_queue = asyncio.Queue()  # shared_state -> tray_control

    # Create units for tray mode (no keyboard listener)
    sound_recorder = DummySoundRecorder(
        config={"sample_rate": 44100}, audio_output_queue=audio_pipeline_queue
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

    # Simulate tray-driven events
    async def tray_event_simulator():
        """Simulate tray-driven events and state changes."""
        await asyncio.sleep(2)

        # Simulate user action via tray (e.g., start recording)
        await state_updates_queue.put("tray_event:start_recording")
        await sound_recorder.control_queue.put("start_recording")
        logger.info("Tray mode: Simulated tray start recording action")

        # Update state to show recording
        await state_updates_queue.put("state_change:recording")

        # Let recording run
        await asyncio.sleep(4)

        # Simulate stop recording
        await state_updates_queue.put("tray_event:stop_recording")
        await sound_recorder.control_queue.put("stop_recording")
        logger.info("Tray mode: Simulated tray stop recording action")

        # Update state to show done
        await state_updates_queue.put("state_change:done")

        # Simulate tray exit after processing
        await asyncio.sleep(2)
        await state_updates_queue.put("tray_event:exit")

    # Start all units
    units = [
        sound_recorder,
        noise_cancelling,
        voice_recognition,
        output_handler,
        shared_state,
        tray_control,
    ]

    logger.info("Starting tray mode units...")
    tasks = [asyncio.create_task(unit.run()) for unit in units]
    tray_simulator_task = asyncio.create_task(tray_event_simulator())

    # Let the system run (tray mode stays alive until explicitly exited)
    logger.info("Tray mode running - tray icon reflects state changes...")
    await asyncio.sleep(10)

    # Clean shutdown
    logger.info("Tray mode shutting down...")

    # Stop all units
    for unit in units:
        if hasattr(unit, "stop"):
            unit.stop()

    # Cancel all tasks
    tray_simulator_task.cancel()
    for task in tasks:
        task.cancel()

    # Wait for all tasks to complete
    await asyncio.gather(tray_simulator_task, *tasks, return_exceptions=True)

    logger.info("Tray mode completed")


if __name__ == "__main__":
    asyncio.run(main())
