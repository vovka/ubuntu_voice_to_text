"""
Dummy tray control implementation for testing and integration verification.

This implementation logs all activity and demonstrates queue interaction
without real tray functionality.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from interfaces.tray_control import ITrayControl
from interfaces.queue_protocol import QueueProtocol

logger = logging.getLogger(__name__)


class DummyTrayControl(ITrayControl):
    """
    Dummy implementation of ITrayControl that logs activity and demonstrates queue interaction.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        input_queue: Optional[QueueProtocol] = None,
    ):
        """Initialize dummy tray control with optional configuration and external queue."""
        self._config = config or {}
        self._input_queue = input_queue if input_queue else asyncio.Queue()
        self._running = False
        logger.info(
            f"DummyTrayControl initialized with config: {self._config}, using input_queue: {id(self._input_queue)}"
        )

    @property
    def input_queue(self) -> QueueProtocol:
        """Return the input queue for commands or state updates."""
        return self._input_queue

    async def run(self) -> None:
        """
        Main async loop to demonstrate tray control and queue activity.
        """
        logger.info("DummyTrayControl.run() started")
        self._running = True

        try:
            while self._running:
                try:
                    # Wait for input commands with timeout
                    command = await asyncio.wait_for(
                        self._input_queue.get(), timeout=1.5
                    )
                    logger.info(f"DummyTrayControl processed command: {command}")
                except asyncio.TimeoutError:
                    # Periodically log activity to show the unit is alive
                    logger.info("DummyTrayControl is alive - no commands received")

        except asyncio.CancelledError:
            logger.info("DummyTrayControl.run() cancelled")
            self._running = False
            raise
        except Exception as e:
            logger.error(f"DummyTrayControl.run() error: {e}")
            raise
        finally:
            logger.info("DummyTrayControl.run() stopped")

    def stop(self) -> None:
        """Stop the running loop."""
        self._running = False
        logger.info("DummyTrayControl stop requested")
