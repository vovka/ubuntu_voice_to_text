"""
Audio Pipeline package for decoupled voice typing processing.

This package contains the pipeline stages and coordination logic
for separating audio capture, buffering, and recognition into
independent components.
"""

from .interfaces import AudioPipelineStage, PipelineCoordinator
from .stages import AudioCaptureStage, AudioBufferingStage, RecognitionStage
from .coordinator import AudioPipelineCoordinator
from .audio_input import SoundDeviceAudioInput

__all__ = [
    "AudioPipelineStage",
    "PipelineCoordinator", 
    "AudioCaptureStage",
    "AudioBufferingStage",
    "RecognitionStage",
    "AudioPipelineCoordinator",
    "SoundDeviceAudioInput",
]