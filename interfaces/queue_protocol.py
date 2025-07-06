"""
Queue protocol for async communication between units.

This protocol defines the contract for queue implementations used
throughout the application for inter-unit communication.
"""

from typing import Any, Protocol


class QueueProtocol(Protocol):
    """
    A generic queue protocol for async communication between units.
    Implementations must provide async put() and get() methods.
    """

    async def put(self, item: Any) -> None:
        """Put an item into the queue."""
        ...

    async def get(self) -> Any:
        """Get an item from the queue."""
        ...
