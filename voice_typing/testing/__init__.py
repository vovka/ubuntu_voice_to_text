"""
Testing utilities and mock implementations for voice typing system.

This package provides reusable mock implementations for all interfaces
to enable isolated unit testing of modules.
"""

from .mocks import (
    MockAudioInputSource,
    MockVoiceRecognitionSource,
    MockOutputActionTarget,
    MockStateManager,
)

__all__ = [
    "MockAudioInputSource",
    "MockVoiceRecognitionSource", 
    "MockOutputActionTarget",
    "MockStateManager",
]