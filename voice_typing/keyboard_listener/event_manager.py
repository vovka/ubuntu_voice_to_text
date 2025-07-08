"""
Event manager for keyboard listener events.

This module handles event generation and state management for the
keyboard listener, separating event logic from hotkey detection.
"""

import asyncio
import logging
from typing import Optional

from interfaces.queue_protocol import QueueProtocol

logger = logging.getLogger(__name__)


class EventManager:
    """
    Manages keyboard event generation and state toggling.
    
    Handles the toggle state for recording start/stop events and
    queues them to the output queue.
    """

    def __init__(self, output_queue: QueueProtocol):
        """Initialize event manager with output queue."""
        self._output_queue = output_queue
        self._recording_state = False

    async def send_toggle_event(self) -> None:
        """Send toggle event based on current recording state."""
        if self._recording_state:
            event = "ctrl+shift+stop_recording"
            self._recording_state = False
        else:
            event = "ctrl+shift+start_recording"
            self._recording_state = True
        
        await self._output_queue.put(event)
        logger.info(f"EventManager sent event: {event}")

    async def send_fallback_event(self) -> None:
        """Send fallback event when pynput is not available."""
        event = "ctrl+shift+start_recording"
        await self._output_queue.put(event)
        logger.info(f"EventManager sent fallback event: {event}")