"""
Dummy voice recognition implementation for testing and integration verification.

This implementation logs all activity and demonstrates queue interaction
without real voice recognition functionality.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from interfaces.voice_recognition import IVoiceRecognition
from interfaces.queue_protocol import QueueProtocol

logger = logging.getLogger(__name__)


class DummyVoiceRecognition(IVoiceRecognition):
    """
    Dummy implementation of IVoiceRecognition that logs activity and demonstrates queue interaction.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        audio_input_queue: Optional[QueueProtocol] = None,
        text_output_queue: Optional[QueueProtocol] = None,
    ):
        """Initialize dummy voice recognition with optional configuration and external queues."""
        self._config = config or {}
        self._audio_input_queue = (
            audio_input_queue if audio_input_queue else asyncio.Queue()
        )
        self._text_output_queue = (
            text_output_queue if text_output_queue else asyncio.Queue()
        )
        self._running = False
        logger.info(
            f"DummyVoiceRecognition initialized with config: {self._config}, using audio_input_queue: {id(self._audio_input_queue)}, text_output_queue: {id(self._text_output_queue)}"
        )

    @property
    def audio_input_queue(self) -> QueueProtocol:
        """Return the audio input queue for receiving audio to recognize."""
        return self._audio_input_queue

    @property
    def text_output_queue(self) -> QueueProtocol:
        """Return the text output queue for sending recognized text."""
        return self._text_output_queue

    async def run(self) -> None:
        """
        Main async loop to demonstrate voice recognition and queue activity.
        """
        logger.info("DummyVoiceRecognition.run() started")
        self._running = True

        try:
            while self._running:
                try:
                    # Wait for audio input with timeout
                    audio_chunk = await asyncio.wait_for(
                        self._audio_input_queue.get(), timeout=2.0
                    )
                    logger.info(f"DummyVoiceRecognition received audio: {audio_chunk}")

                    # Simulate voice recognition processing
                    recognized_text = f"recognized_text_from_{audio_chunk}"
                    await self._text_output_queue.put(recognized_text)
                    logger.info(
                        f"DummyVoiceRecognition put recognized text: {recognized_text}"
                    )

                except asyncio.TimeoutError:
                    # Periodically log activity to show the unit is alive
                    logger.info("DummyVoiceRecognition is alive - no audio received")

                    # Simulate putting test audio
                    test_audio = f"test_audio_{asyncio.get_event_loop().time()}"
                    await self._audio_input_queue.put(test_audio)
                    logger.info(f"DummyVoiceRecognition put test audio: {test_audio}")

        except asyncio.CancelledError:
            logger.info("DummyVoiceRecognition.run() cancelled")
            self._running = False
            raise
        except Exception as e:
            logger.error(f"DummyVoiceRecognition.run() error: {e}")
            raise
        finally:
            logger.info("DummyVoiceRecognition.run() stopped")

    def stop(self) -> None:
        """Stop the running loop."""
        self._running = False
        logger.info("DummyVoiceRecognition stop requested")
