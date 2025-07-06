"""
Dummy keyboard listener implementation for testing and integration verification.

This implementation logs all activity and demonstrates queue interaction
without real keyboard listening functionality.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from interfaces.keyboard_listener import IKeyboardListener
from interfaces.queue_protocol import QueueProtocol

logger = logging.getLogger(__name__)


class DummyKeyboardListener(IKeyboardListener):
    """
    Dummy implementation of IKeyboardListener that logs activity and demonstrates queue interaction.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, output_queue: Optional[QueueProtocol] = None):
        """Initialize dummy keyboard listener with optional configuration and external queue."""
        self._config = config or {}
        self._output_queue = output_queue if output_queue else asyncio.Queue()
        self._running = False
        logger.info(f"DummyKeyboardListener initialized with config: {self._config}, using output_queue: {id(self._output_queue)}")
    
    @property
    def output_queue(self) -> QueueProtocol:
        """Return the output queue for publishing detected hotkey events."""
        return self._output_queue
    
    async def run(self) -> None:
        """
        Main async loop to demonstrate keyboard listening and queue activity.
        """
        logger.info("DummyKeyboardListener.run() started")
        self._running = True
        
        try:
            while self._running:
                # Simulate keyboard listening by waiting and then generating events
                await asyncio.sleep(3.0)
                
                if self._running:
                    # Simulate hotkey detection
                    hotkey_event = "ctrl+shift+start_recording"
                    await self._output_queue.put(hotkey_event)
                    logger.info(f"DummyKeyboardListener detected hotkey: {hotkey_event}")
                    
                    # Wait a bit more and simulate another event
                    await asyncio.sleep(2.0)
                    
                    if self._running:
                        hotkey_event = "ctrl+shift+stop_recording"
                        await self._output_queue.put(hotkey_event)
                        logger.info(f"DummyKeyboardListener detected hotkey: {hotkey_event}")
                    
        except asyncio.CancelledError:
            logger.info("DummyKeyboardListener.run() cancelled")
            self._running = False
            raise
        except Exception as e:
            logger.error(f"DummyKeyboardListener.run() error: {e}")
            raise
        finally:
            logger.info("DummyKeyboardListener.run() stopped")
    
    def stop(self) -> None:
        """Stop the running loop."""
        self._running = False
        logger.info("DummyKeyboardListener stop requested")