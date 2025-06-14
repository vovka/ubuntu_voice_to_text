"""
Output Type Enumeration

Defines the types of output targets supported by the voice typing system.
"""

from enum import Enum


class OutputType(Enum):
    """Enumeration of supported output types."""
    KEYBOARD = "keyboard"
    CLIPBOARD = "clipboard"
    FILE = "file"
    CALLBACK = "callback"