"""
Bare Mode main file - No tray, no keyboard.
Scenario 1: The app starts, units are initialized, and they react to internal events
(e.g., voice detection) to record, transcribe, and output, then the application exits.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dummy import *
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    Bare mode: No tray, no keyboard. The app starts, activates recording automatically,
    processes audio through the pipeline, and exits when done.
    """
    logger.info("Starting Bare Mode (No Tray, No Keyboard)")

    # Create shared queues for the audio pipeline
    audio_pipeline_queue = asyncio.Queue()  # sound_recorder -> noise_cancelling
    clean_audio_queue = asyncio.Queue()  # noise_cancelling -> voice_recognition
    recognized_text_queue = asyncio.Queue()  # voice_recognition -> output_handler

    # Create units for bare mode (no keyboard listener or tray control)
    sound_recorder = DummySoundRecorder(
        config={"sample_rate": 44100, "auto_start": True},
        audio_output_queue=audio_pipeline_queue,
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

    # Auto-start recording for bare mode
    async def auto_start_recording():
        """Auto-start recording after a brief delay."""
        await asyncio.sleep(1)
        await sound_recorder.control_queue.put("start_recording")
        logger.info("Auto-started recording in bare mode")

        # Simulate some recording time, then stop
        await asyncio.sleep(5)
        await sound_recorder.control_queue.put("stop_recording")
        logger.info("Auto-stopped recording in bare mode")

    # Start all units
    units = [
        sound_recorder,
        noise_cancelling,
        voice_recognition,
        output_handler,
        shared_state,
    ]

    logger.info("Starting bare mode units...")
    tasks = [asyncio.create_task(unit.run()) for unit in units]
    auto_start_task = asyncio.create_task(auto_start_recording())

    # Let the system run for a limited time (bare mode should exit after processing)
    logger.info("Processing audio in bare mode...")
    await asyncio.sleep(8)

    # Clean shutdown
    logger.info("Bare mode processing complete, shutting down...")

    # Stop all units
    for unit in units:
        if hasattr(unit, "stop"):
            unit.stop()

    # Cancel all tasks
    auto_start_task.cancel()
    for task in tasks:
        task.cancel()

    # Wait for all tasks to complete
    await asyncio.gather(auto_start_task, *tasks, return_exceptions=True)

    logger.info("Bare mode completed and exited")


if __name__ == "__main__":
    asyncio.run(main())
