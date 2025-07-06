"""
Dummy noise cancelling implementation for testing and integration verification.

This implementation logs all activity and demonstrates queue interaction
without real noise cancelling functionality.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from interfaces.noise_cancelling import INoiseCancelling
from interfaces.queue_protocol import QueueProtocol

logger = logging.getLogger(__name__)


class DummyNoiseCancelling(INoiseCancelling):
    """
    Dummy implementation of INoiseCancelling that logs activity and demonstrates queue interaction.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        audio_input_queue: Optional[QueueProtocol] = None,
        audio_output_queue: Optional[QueueProtocol] = None,
    ):
        """Initialize dummy noise cancelling with optional configuration and external queues."""
        self._config = config or {}
        self._audio_input_queue = (
            audio_input_queue if audio_input_queue else asyncio.Queue()
        )
        self._audio_output_queue = (
            audio_output_queue if audio_output_queue else asyncio.Queue()
        )
        self._running = False
        logger.info(
            f"DummyNoiseCancelling initialized with config: {self._config}, using audio_input_queue: {id(self._audio_input_queue)}, audio_output_queue: {id(self._audio_output_queue)}"
        )

    @property
    def audio_input_queue(self) -> QueueProtocol:
        """Return the audio input queue for receiving raw audio."""
        return self._audio_input_queue

    @property
    def audio_output_queue(self) -> QueueProtocol:
        """Return the audio output queue for sending processed audio."""
        return self._audio_output_queue

    async def run(self) -> None:
        """
        Main async loop to demonstrate noise cancelling and queue activity.
        """
        logger.info("DummyNoiseCancelling.run() started")
        self._running = True

        try:
            while self._running:
                try:
                    # Wait for audio input with timeout
                    raw_audio = await asyncio.wait_for(
                        self._audio_input_queue.get(), timeout=1.5
                    )
                    logger.info(f"DummyNoiseCancelling received raw audio: {raw_audio}")

                    # Simulate noise cancelling processing
                    processed_audio = f"clean_{raw_audio}"
                    await self._audio_output_queue.put(processed_audio)
                    logger.info(
                        f"DummyNoiseCancelling put processed audio: {processed_audio}"
                    )

                except asyncio.TimeoutError:
                    # Periodically log activity to show the unit is alive
                    logger.info("DummyNoiseCancelling is alive - no audio received")

                    # Simulate putting test audio
                    test_audio = f"test_raw_audio_{asyncio.get_event_loop().time()}"
                    await self._audio_input_queue.put(test_audio)
                    logger.info(
                        f"DummyNoiseCancelling put test raw audio: {test_audio}"
                    )

        except asyncio.CancelledError:
            logger.info("DummyNoiseCancelling.run() cancelled")
            self._running = False
            raise
        except Exception as e:
            logger.error(f"DummyNoiseCancelling.run() error: {e}")
            raise
        finally:
            logger.info("DummyNoiseCancelling.run() stopped")

    def stop(self) -> None:
        """Stop the running loop."""
        self._running = False
        logger.info("DummyNoiseCancelling stop requested")
