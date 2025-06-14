"""
Pipeline coordinator for managing audio processing stages.

Coordinates the execution of pipeline stages and manages queues between them.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from .interfaces import PipelineCoordinator, AudioPipelineStage
from .stages import AudioCaptureStage, AudioBufferingStage, RecognitionStage
from ..interfaces import AudioInputSource, VoiceRecognitionSource


class AudioPipelineCoordinator(PipelineCoordinator):
    """
    Coordinates the audio processing pipeline stages.
    
    Manages the flow of data between capture, buffering, and recognition stages
    using async queues for communication.
    """

    def __init__(
        self,
        audio_input: AudioInputSource,
        recognition_source: VoiceRecognitionSource,
        output_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize the pipeline coordinator.

        Args:
            audio_input: Audio input source for capture stage
            recognition_source: Recognition source for recognition stage
            output_callback: Optional callback for recognized text output
        """
        self._audio_input = audio_input
        self._recognition_source = recognition_source
        self._output_callback = output_callback
        
        # Pipeline stages
        self._capture_stage: Optional[AudioCaptureStage] = None
        self._buffering_stage: Optional[AudioBufferingStage] = None
        self._recognition_stage: Optional[RecognitionStage] = None
        
        # Queues for inter-stage communication
        self._capture_to_buffer_queue: Optional[asyncio.Queue] = None
        self._buffer_to_recognition_queue: Optional[asyncio.Queue] = None
        
        self._running = False
        self._config: Optional[Dict[str, Any]] = None

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the pipeline coordinator and all stages.

        Args:
            config: Configuration dictionary for the pipeline

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        self._config = config
        
        # Create queues for inter-stage communication
        queue_size = config.get('queue_size', 100)
        self._capture_to_buffer_queue = asyncio.Queue(maxsize=queue_size)
        self._buffer_to_recognition_queue = asyncio.Queue(maxsize=queue_size)
        
        # Create pipeline stages
        self._capture_stage = AudioCaptureStage(self._audio_input)
        self._buffering_stage = AudioBufferingStage(
            buffer_size=config.get('buffer_size', 10)
        )
        self._recognition_stage = RecognitionStage(
            self._recognition_source,
            self._output_callback
        )
        
        # Connect stages with queues
        self._capture_stage.set_output_queue(self._capture_to_buffer_queue)
        self._buffering_stage.set_input_queue(self._capture_to_buffer_queue)
        self._buffering_stage.set_output_queue(self._buffer_to_recognition_queue)
        self._recognition_stage.set_input_queue(self._buffer_to_recognition_queue)
        
        # Initialize all stages
        stages_initialized = [
            await self._capture_stage.initialize(config),
            await self._buffering_stage.initialize(config),
            await self._recognition_stage.initialize(config)
        ]
        
        return all(stages_initialized)

    async def start_pipeline(self) -> bool:
        """
        Start all pipeline stages.

        Returns:
            bool: True if pipeline started successfully, False otherwise
        """
        if self._running:
            return True
            
        if not all([self._capture_stage, self._buffering_stage, self._recognition_stage]):
            return False
        
        # Start stages in order: recognition, buffering, then capture
        # This ensures downstream stages are ready before upstream starts sending data
        stages_started = [
            await self._recognition_stage.start(),
            await self._buffering_stage.start(),
            await self._capture_stage.start()
        ]
        
        if all(stages_started):
            self._running = True
            return True
        else:
            # If any stage failed to start, stop the ones that did start
            await self.stop_pipeline()
            return False

    async def stop_pipeline(self) -> None:
        """
        Stop all pipeline stages.
        """
        if not self._running:
            return
            
        self._running = False
        
        # Stop stages in reverse order: capture, buffering, then recognition
        if self._capture_stage:
            await self._capture_stage.stop()
        if self._buffering_stage:
            await self._buffering_stage.stop()
        if self._recognition_stage:
            await self._recognition_stage.stop()

    def is_pipeline_running(self) -> bool:
        """
        Check if the pipeline is currently running.

        Returns:
            bool: True if pipeline is running, False otherwise
        """
        if not self._running:
            return False
            
        # Check if all stages are running
        return all([
            stage.is_running() if stage else False
            for stage in [self._capture_stage, self._buffering_stage, self._recognition_stage]
        ])

    async def cleanup(self) -> None:
        """
        Clean up all pipeline resources.
        """
        await self.stop_pipeline()
        
        # Clean up all stages
        if self._capture_stage:
            await self._capture_stage.cleanup()
        if self._buffering_stage:
            await self._buffering_stage.cleanup()
        if self._recognition_stage:
            await self._recognition_stage.cleanup()
            
        # Clear queues
        if self._capture_to_buffer_queue:
            while not self._capture_to_buffer_queue.empty():
                try:
                    self._capture_to_buffer_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                    
        if self._buffer_to_recognition_queue:
            while not self._buffer_to_recognition_queue.empty():
                try:
                    self._buffer_to_recognition_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

    def get_stage_status(self) -> Dict[str, bool]:
        """
        Get the running status of each pipeline stage.

        Returns:
            Dict[str, bool]: Status of each stage
        """
        return {
            'capture': self._capture_stage.is_running() if self._capture_stage else False,
            'buffering': self._buffering_stage.is_running() if self._buffering_stage else False,
            'recognition': self._recognition_stage.is_running() if self._recognition_stage else False,
        }