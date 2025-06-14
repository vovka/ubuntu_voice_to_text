"""
Output Dispatcher

Manages delivery of recognized text to multiple output targets.
Provides event-based architecture for output handling.
"""

import time
from typing import Dict, Any, Optional, List, Callable
from .output_action_target import OutputActionTarget
from .output_type import OutputType


class OutputDispatcher:
    """
    Dispatcher that manages delivery of recognized text to multiple output targets.
    
    This class decouples recognition logic from output handling by providing
    an event-based architecture where output targets can be registered and
    will receive text events.
    """

    def __init__(self):
        """Initialize the output dispatcher."""
        self._targets: List[OutputActionTarget] = []
        self._event_listeners: List[Callable[[str, Optional[Dict[str, Any]]], None]] = []
        self._initialized = False

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Initialize the dispatcher with configuration.

        Args:
            config: Optional configuration dictionary

        Returns:
            bool: True if initialization was successful
        """
        self._initialized = True
        return True

    def add_target(self, target: OutputActionTarget) -> bool:
        """
        Add an output target to the dispatcher.

        Args:
            target: Output target to add

        Returns:
            bool: True if target was added successfully
        """
        if not target.is_available():
            return False
        
        self._targets.append(target)
        return True

    def remove_target(self, target: OutputActionTarget) -> bool:
        """
        Remove an output target from the dispatcher.

        Args:
            target: Output target to remove

        Returns:
            bool: True if target was removed successfully
        """
        try:
            self._targets.remove(target)
            return True
        except ValueError:
            return False

    def add_event_listener(self, listener: Callable[[str, Optional[Dict[str, Any]]], None]) -> None:
        """
        Add an event listener for text events.

        Args:
            listener: Function to call when text is dispatched
        """
        self._event_listeners.append(listener)

    def remove_event_listener(self, listener: Callable[[str, Optional[Dict[str, Any]]], None]) -> bool:
        """
        Remove an event listener.

        Args:
            listener: Function to remove

        Returns:
            bool: True if listener was removed successfully
        """
        try:
            self._event_listeners.remove(listener)
            return True
        except ValueError:
            return False

    def dispatch_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Dispatch recognized text to all registered targets and listeners.

        Args:
            text: The recognized text to dispatch
            metadata: Optional metadata about the recognition

        Returns:  
            bool: True if at least one target successfully received the text
        """
        if not self._initialized:
            return False

        if not text:
            return False

        # Add timestamp to metadata if not present
        if metadata is None:
            metadata = {}
        if 'timestamp' not in metadata:
            metadata['timestamp'] = time.time()

        success_count = 0

        # Dispatch to all registered targets
        for target in self._targets:
            try:
                if target.is_available() and target.deliver_text(text, metadata):
                    success_count += 1
            except Exception as e:
                print(f"[OutputDispatcher] Error delivering text to target {target}: {e}")

        # Notify all event listeners
        for listener in self._event_listeners:
            try:
                listener(text, metadata)
            except Exception as e:
                print(f"[OutputDispatcher] Error notifying listener {listener}: {e}")

        return success_count > 0

    def get_target_count(self) -> int:
        """
        Get the number of registered targets.

        Returns:
            int: Number of registered targets
        """
        return len(self._targets)

    def get_targets_by_type(self, output_type: OutputType) -> List[OutputActionTarget]:
        """
        Get all targets of a specific type.

        Args:
            output_type: Type of output targets to retrieve

        Returns:
            List[OutputActionTarget]: List of targets matching the type
        """
        return [target for target in self._targets if target.get_output_type() == output_type]

    def clear_targets(self) -> None:
        """Remove all registered targets."""
        self._targets.clear()

    def clear_listeners(self) -> None:
        """Remove all registered event listeners."""
        self._event_listeners.clear()

    def cleanup(self) -> None:
        """Clean up all resources."""
        # Cleanup all targets
        for target in self._targets:
            try:
                target.cleanup()
            except Exception as e:
                print(f"[OutputDispatcher] Error cleaning up target {target}: {e}")
        
        self.clear_targets()
        self.clear_listeners()
        self._initialized = False

    def is_initialized(self) -> bool:
        """
        Check if the dispatcher is initialized.

        Returns:
            bool: True if initialized
        """
        return self._initialized