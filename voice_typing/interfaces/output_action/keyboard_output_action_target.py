"""
Keyboard Output Action Target

Output target that types text using keyboard simulation.
"""

import subprocess
from typing import Dict, Any, Optional

from .output_action_target import OutputActionTarget
from .output_type import OutputType


class KeyboardOutputActionTarget(OutputActionTarget):
    """
    Output target that types text using keyboard simulation.
    
    Uses xdotool for keyboard input simulation on Linux.
    """

    def __init__(self):
        """Initialize the keyboard output target."""
        self._initialized = False
        self._append_space = True

    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the keyboard output target.

        Args:
            config: Configuration dictionary that may contain:
                - append_space: Whether to append space after text (default: True)

        Returns:
            bool: True if initialization was successful
        """
        self._append_space = config.get('append_space', True)
        self._initialized = self.is_available()
        return self._initialized

    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Type the text using keyboard simulation.

        Args:
            text: The text to type
            metadata: Optional metadata (ignored for keyboard output)

        Returns:
            bool: True if text was typed successfully
        """
        if not self._initialized or not text:
            return False

        try:
            output_text = text
            if self._append_space:
                output_text += " "
            
            result = subprocess.run(
                ["xdotool", "type", output_text],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("[KeyboardOutputActionTarget] Timeout while typing text")
            return False
        except Exception as e:
            print(f"[KeyboardOutputActionTarget] Error typing text: {e}")
            return False

    def is_available(self) -> bool:
        """
        Check if xdotool is available for keyboard simulation.

        Returns:
            bool: True if xdotool is available
        """
        try:
            result = subprocess.run(
                ["which", "xdotool"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def get_output_type(self) -> OutputType:
        """
        Get the output type.

        Returns:
            OutputType: KEYBOARD output type
        """
        return OutputType.KEYBOARD

    def supports_formatting(self) -> bool:
        """
        Check if formatting is supported.

        Returns:
            bool: False - keyboard output doesn't support formatting
        """
        return False

    def cleanup(self) -> None:
        """Clean up resources (no cleanup needed for keyboard output)."""
        self._initialized = False