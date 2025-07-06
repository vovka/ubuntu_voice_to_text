"""
Dummy shared state implementation for testing and integration verification.

This implementation logs all activity and demonstrates queue interaction
without real state management functionality.
"""

import asyncio
import logging
from interfaces.shared_state import ISharedState
from interfaces.queue_protocol import QueueProtocol

logger = logging.getLogger(__name__)


class DummySharedState(ISharedState):
    """
    Dummy implementation of ISharedState that logs activity and demonstrates queue interaction.
    """
    
    def __init__(self):
        """Initialize dummy shared state with an async queue."""
        self._state_queue = asyncio.Queue()
        self._running = False
        logger.info("DummySharedState initialized")
    
    @property
    def state_queue(self) -> QueueProtocol:
        """Return the state queue for state change events."""
        return self._state_queue
    
    async def run(self) -> None:
        """
        Main async loop to demonstrate state management and queue activity.
        """
        logger.info("DummySharedState.run() started")
        self._running = True
        
        try:
            while self._running:
                try:
                    # Wait for state change events with timeout
                    state_event = await asyncio.wait_for(
                        self._state_queue.get(), timeout=2.0
                    )
                    logger.info(f"DummySharedState processed state event: {state_event}")
                except asyncio.TimeoutError:
                    # Periodically log activity to show the unit is alive
                    logger.info("DummySharedState is alive - no state events received")
                    
                    # Simulate putting a test state event
                    await self._state_queue.put("test_state_event")
                    logger.info("DummySharedState put test state event")
                    
        except asyncio.CancelledError:
            logger.info("DummySharedState.run() cancelled")
            self._running = False
            raise
        except Exception as e:
            logger.error(f"DummySharedState.run() error: {e}")
            raise
        finally:
            logger.info("DummySharedState.run() stopped")
    
    def stop(self) -> None:
        """Stop the running loop."""
        self._running = False
        logger.info("DummySharedState stop requested")