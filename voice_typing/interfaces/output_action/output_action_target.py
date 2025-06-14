"""
Output Action Target Interface

Abstract base class for output actions that deliver recognized text
to various targets (keyboard, clipboard, file, etc.).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from .output_type import OutputType


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