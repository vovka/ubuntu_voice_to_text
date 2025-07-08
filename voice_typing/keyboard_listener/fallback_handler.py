"""
Fallback mode handler for environments without pynput support.

This module provides fallback functionality when pynput cannot be used,
such as in CI environments or containers without X server access.
"""

import asyncio
import logging

from .event_manager import EventManager

logger = logging.getLogger(__name__)


class FallbackHandler:
    """
    Handles fallback mode when pynput is not available.
    
    Provides basic functionality to send test events in environments
    where pynput cannot access the display server.
    """

    def __init__(self, event_manager: EventManager):
        """Initialize fallback handler with event manager."""
        self._event_manager = event_manager
        self._running = False

    async def run_fallback_mode(self) -> None:
        """Run fallback mode by sending a test event after delay."""
        logger.warning("Running in fallback mode without pynput")
        await asyncio.sleep(5.0)
        
        if self._running:
            await self._event_manager.send_fallback_event()

    def start(self) -> None:
        """Start fallback mode."""
        self._running = True

    def stop(self) -> None:
        """Stop fallback mode."""
        self._running = False