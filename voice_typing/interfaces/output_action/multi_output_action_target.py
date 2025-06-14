"""
Multi Output Action Target

Output action target that can deliver to multiple targets simultaneously.
This allows for composing multiple output targets (e.g., keyboard + clipboard)
into a single output action.
"""

from typing import Dict, Any, Optional, List

from .output_action_target import OutputActionTarget
from .output_type import OutputType


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