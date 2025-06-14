"""
Output Action Interface

Abstract base class for output actions that deliver recognized text
to various targets (keyboard, clipboard, file, etc.).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum


class OutputType(Enum):
    """Enumeration of supported output types."""
    KEYBOARD = "keyboard"
    CLIPBOARD = "clipboard"
    FILE = "file"
    CALLBACK = "callback"


class OutputActionTarget(ABC):
    """
    Abstract base class for output action targets.
    
    This interface defines the contract that all output implementations
    must follow to deliver recognized text to their target destination.
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the output action target with configuration.

        Args:
            config: Configuration dictionary containing parameters like:
                - output_type: Type of output (OutputType enum value)
                - target: Target specification (file path, callback, etc.)
                - formatting: Text formatting options
                - append_space: Whether to append space after text

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass

    @abstractmethod
    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Deliver recognized text to the target.

        Args:
            text: The recognized text to deliver
            metadata: Optional metadata about the recognition (confidence, timestamp, etc.)

        Returns:
            bool: True if delivery was successful, False otherwise
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the output target is available for use.

        Returns:
            bool: True if available, False otherwise
        """
        pass

    @abstractmethod
    def get_output_type(self) -> OutputType:
        """
        Get the type of output this target provides.

        Returns:
            OutputType: The type of output this target handles
        """
        pass

    @abstractmethod
    def supports_formatting(self) -> bool:
        """
        Check if this output target supports text formatting.

        Returns:
            bool: True if formatting is supported, False otherwise
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up resources used by the output target.
        """
        pass


class MultiOutputActionTarget(OutputActionTarget):
    """
    Output action target that can deliver to multiple targets simultaneously.
    
    This allows for composing multiple output targets (e.g., keyboard + clipboard)
    into a single output action.
    """

    def __init__(self, targets: List[OutputActionTarget]):
        """
        Initialize with a list of output targets.
        
        Args:
            targets: List of OutputActionTarget instances to deliver to
        """
        self._targets = targets
        self._initialized = False

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize all configured targets."""
        success = True
        for target in self._targets:
            if not target.initialize(config):
                success = False
        self._initialized = success
        return success

    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Deliver text to all configured targets."""
        if not self._initialized:
            return False
            
        success = True
        for target in self._targets:
            if not target.deliver_text(text, metadata):
                success = False
        return success

    def is_available(self) -> bool:
        """Check if at least one target is available."""
        return any(target.is_available() for target in self._targets)

    def get_output_type(self) -> OutputType:
        """Return the first target's output type."""
        return self._targets[0].get_output_type() if self._targets else OutputType.CALLBACK

    def supports_formatting(self) -> bool:
        """Check if any target supports formatting."""
        return any(target.supports_formatting() for target in self._targets)

    def cleanup(self) -> None:
        """Clean up all targets."""
        for target in self._targets:
            target.cleanup()


class CallbackOutputActionTarget(OutputActionTarget):
    """
    Simple output target that calls a provided callback function.
    
    This is useful for testing or custom output handling.
    """

    def __init__(self, callback=None):
        """
        Initialize with an optional callback function.
        
        Args:
            callback: Function to call with (text, metadata) arguments
        """
        self._callback = callback
        self._initialized = False

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the callback target."""
        if 'callback' in config:
            self._callback = config['callback']
        self._initialized = self._callback is not None
        return self._initialized

    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Call the callback with the text."""
        if not self._initialized or not self._callback:
            return False
        try:
            self._callback(text, metadata)
            return True
        except Exception as e:
            print(f"[CallbackOutputActionTarget] Error calling callback: {e}")
            return False

    def is_available(self) -> bool:
        """Check if callback is available."""
        return self._callback is not None

    def get_output_type(self) -> OutputType:
        """Return callback output type."""
        return OutputType.CALLBACK

    def supports_formatting(self) -> bool:
        """Callback targets don't support formatting by default."""
        return False

    def cleanup(self) -> None:
        """No cleanup needed for callback target."""
        pass