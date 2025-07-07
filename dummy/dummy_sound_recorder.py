"""
Dummy sound recorder implementation for testing and integration verification.

This implementation logs all activity and demonstrates queue interaction
without real audio recording functionality.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from interfaces.sound_recorder import ISoundRecorder
from interfaces.queue_protocol import QueueProtocol

logger = logging.getLogger(__name__)


class DummySoundRecorder(ISoundRecorder):
    """
    Dummy implementation of ISoundRecorder that logs activity and demonstrates queue interaction.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        audio_output_queue: Optional[QueueProtocol] = None,
        control_queue: Optional[QueueProtocol] = None,
    ):
        """Initialize dummy sound recorder with optional configuration and external queues."""
        self._config = config or {}
        self._audio_output_queue = (
            audio_output_queue if audio_output_queue else asyncio.Queue()
        )
        self._control_queue = control_queue if control_queue else asyncio.Queue()
        self._running = False
        self._recording = False
        logger.info(
            f"DummySoundRecorder initialized with config: {self._config}, using audio_output_queue: {id(self._audio_output_queue)}, control_queue: {id(self._control_queue)}"
        )

    @property
    def audio_output_queue(self) -> QueueProtocol:
        """Return the audio output queue for sending audio chunks."""
        return self._audio_output_queue

    @property
    def control_queue(self) -> QueueProtocol:
        """Return the control queue for receiving control commands."""
        return self._control_queue

    async def run(self) -> None:
        """
        Main async loop to demonstrate sound recording and queue activity.
        """
        logger.info("DummySoundRecorder.run() started")
        self._running = True

        try:
            while self._running:
                try:
                    # Wait for control commands with timeout
                    control_command = await asyncio.wait_for(
                        self._control_queue.get(), timeout=1.0
                    )
                    logger.info(
                        f"DummySoundRecorder received control command: {control_command}"
                    )

                    # Process control commands
                    if control_command == "start_recording":
                        self._recording = True
                        logger.info("DummySoundRecorder started recording")
                    elif control_command == "stop_recording":
                        self._recording = False
                        logger.info("DummySoundRecorder stopped recording")

                except asyncio.TimeoutError:
                    # Periodically log activity and simulate audio if recording
                    logger.info(
                        f"DummySoundRecorder is alive - recording: {self._recording}"
                    )

                    if self._recording:
                        # Simulate audio chunk
                        audio_chunk = (
                            f"dummy_audio_chunk_{asyncio.get_event_loop().time()}"
                        )
                        await self._audio_output_queue.put(audio_chunk)
                        logger.info(
                            f"DummySoundRecorder put audio chunk: {audio_chunk}"
                        )

        except asyncio.CancelledError:
            logger.info("DummySoundRecorder.run() cancelled")
            self._running = False
            raise
        except Exception as e:
            logger.error(f"DummySoundRecorder.run() error: {e}")
            raise
        finally:
            logger.info("DummySoundRecorder.run() stopped")

    def stop(self) -> None:
        """Stop the running loop."""
        self._running = False
        logger.info("DummySoundRecorder stop requested")
