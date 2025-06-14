"""
Callback Output Action Target

Simple output target that calls a provided callback function.
This is useful for testing or custom output handling.
"""

from typing import Dict, Any, Optional

from .output_action_target import OutputActionTarget
from .output_type import OutputType


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