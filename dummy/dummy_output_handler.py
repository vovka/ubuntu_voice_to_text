"""
Dummy output handler implementation for testing and integration verification.

This implementation logs all activity and demonstrates queue interaction
without real output handling functionality.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from interfaces.output_handler import IOutputHandler
from interfaces.queue_protocol import QueueProtocol

logger = logging.getLogger(__name__)


class DummyOutputHandler(IOutputHandler):
    """
    Dummy implementation of IOutputHandler that logs activity and demonstrates queue interaction.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        input_queue: Optional[QueueProtocol] = None,
    ):
        """Initialize dummy output handler with optional configuration and external queue."""
        self._config = config or {}
        self._input_queue = input_queue if input_queue else asyncio.Queue()
        self._running = False
        logger.info(
            f"DummyOutputHandler initialized with config: {self._config}, using input_queue: {id(self._input_queue)}"
        )

    @property
    def input_queue(self) -> QueueProtocol:
        """Return the input queue for receiving recognized text."""
        return self._input_queue

    async def run(self) -> None:
        """
        Main async loop to demonstrate output handling and queue activity.
        """
        logger.info("DummyOutputHandler.run() started")
        self._running = True

        try:
            while self._running:
                try:
                    # Wait for recognized text with timeout
                    recognized_text = await asyncio.wait_for(
                        self._input_queue.get(), timeout=1.8
                    )
                    logger.info(f"DummyOutputHandler received text: {recognized_text}")

                    # Simulate output handling (clipboard, active window, etc.)
                    logger.info(
                        f"DummyOutputHandler delivered text to output: {recognized_text}"
                    )

                except asyncio.TimeoutError:
                    # Periodically log activity to show the unit is alive
                    logger.info("DummyOutputHandler is alive - no text received")

        except asyncio.CancelledError:
            logger.info("DummyOutputHandler.run() cancelled")
            self._running = False
            raise
        except Exception as e:
            logger.error(f"DummyOutputHandler.run() error: {e}")
            raise
        finally:
            logger.info("DummyOutputHandler.run() stopped")

    def stop(self) -> None:
        """Stop the running loop."""
        self._running = False
        logger.info("DummyOutputHandler stop requested")
