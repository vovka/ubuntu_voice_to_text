from dummy import *
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_integration():
    # Create all dummy units
    units = [
        DummySharedState(),
        DummyTrayControl(),
        DummyKeyboardListener(),
        DummySoundRecorder(),
        DummyNoiseCancelling(),
        DummyVoiceRecognition(),
        DummyOutputHandler(),
    ]

    # Run all units concurrently
    tasks = [asyncio.create_task(unit.run()) for unit in units]

    # Let them run for a while
    await asyncio.sleep(5)

    # Cancel all tasks
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

asyncio.run(test_integration())
