from dummy import *
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """
    Main async function that wires dummy units together with shared queues
    and demonstrates inter-unit communication.
    """
    logger.info("Starting main demo with inter-unit communication")
    
    # Create shared queues for inter-unit communication
    hotkey_events_queue = asyncio.Queue()  # keyboard_listener -> sound_recorder, shared_state
    sound_control_queue = asyncio.Queue()  # receives control commands for sound_recorder
    audio_pipeline_queue = asyncio.Queue()  # sound_recorder -> noise_cancelling
    clean_audio_queue = asyncio.Queue()  # noise_cancelling -> voice_recognition
    recognized_text_queue = asyncio.Queue()  # voice_recognition -> output_handler
    state_updates_queue = asyncio.Queue()  # shared_state -> tray_control
    
    # Create dummy units with shared queues
    keyboard_listener = DummyKeyboardListener(
        config={"hotkeys": ["ctrl+shift"]},
        output_queue=hotkey_events_queue
    )
    
    sound_recorder = DummySoundRecorder(
        config={"sample_rate": 44100},
        audio_output_queue=audio_pipeline_queue,
        control_queue=sound_control_queue
    )
    
    noise_cancelling = DummyNoiseCancelling(
        config={"noise_level": 0.5},
        audio_input_queue=audio_pipeline_queue,
        audio_output_queue=clean_audio_queue
    )
    
    voice_recognition = DummyVoiceRecognition(
        config={"engine": "vosk"},
        audio_input_queue=clean_audio_queue,
        text_output_queue=recognized_text_queue
    )
    
    output_handler = DummyOutputHandler(
        config={"output_type": "clipboard"},
        input_queue=recognized_text_queue
    )
    
    shared_state = DummySharedState(
        state_queue=state_updates_queue
    )
    
    tray_control = DummyTrayControl(
        config={"tray_style": "gnome"},
        input_queue=state_updates_queue
    )
    
    # Create a bridge task to forward hotkey events to sound recorder control
    async def bridge_hotkey_to_sound_control():
        """Bridge task to forward hotkey events to sound recorder control queue."""
        while True:
            try:
                hotkey_event = await hotkey_events_queue.get()
                logger.info(f"Bridge: Forwarding hotkey event '{hotkey_event}' to sound recorder")
                
                # Convert hotkey events to sound recorder control commands
                if "start_recording" in hotkey_event:
                    await sound_control_queue.put("start_recording")
                elif "stop_recording" in hotkey_event:
                    await sound_control_queue.put("stop_recording")
                
                # Also forward to shared state for state tracking
                await state_updates_queue.put(f"hotkey_event:{hotkey_event}")
                
            except asyncio.CancelledError:
                logger.info("Bridge: Hotkey to sound control bridge stopped")
                break
    
    # Start all units and the bridge
    units = [
        keyboard_listener,
        sound_recorder,
        noise_cancelling,
        voice_recognition,
        output_handler,
        shared_state,
        tray_control
    ]
    
    logger.info("Starting all units and bridge...")
    tasks = [asyncio.create_task(unit.run()) for unit in units]
    bridge_task = asyncio.create_task(bridge_hotkey_to_sound_control())
    
    # Let the system run and demonstrate interactions
    logger.info("Letting system run for 10 seconds to demonstrate interactions...")
    await asyncio.sleep(10)
    
    # Clean shutdown
    logger.info("Shutting down...")
    
    # Stop all units
    for unit in units:
        if hasattr(unit, 'stop'):
            unit.stop()
    
    # Cancel all tasks
    bridge_task.cancel()
    for task in tasks:
        task.cancel()
    
    # Wait for all tasks to complete
    await asyncio.gather(bridge_task, *tasks, return_exceptions=True)
    
    logger.info("Main demo completed")

if __name__ == "__main__":
    asyncio.run(main())
