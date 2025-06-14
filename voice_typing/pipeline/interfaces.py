"""
Pipeline interfaces for decoupled audio processing.

Defines the contracts for pipeline stages and coordination.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio


class AudioPipelineStage(ABC):
    """
    Abstract base class for audio pipeline stages.
    
    Each stage processes data and passes it to the next stage via queues.
    """

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the pipeline stage with configuration.

        Args:
            config: Configuration dictionary for the stage

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass

    @abstractmethod
    async def start(self) -> bool:
        """
        Start the pipeline stage processing.

        Returns:
            bool: True if started successfully, False otherwise
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        Stop the pipeline stage processing.
        """
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the pipeline stage is currently running.

        Returns:
            bool: True if running, False otherwise
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up resources used by the pipeline stage.
        """
        pass

    def set_input_queue(self, queue: Optional[asyncio.Queue]) -> None:
        """
        Set the input queue for this stage.

        Args:
            queue: Input queue to receive data from, or None if this is the first stage
        """
        # Subclasses should override this if they need input queues
        pass

    def set_output_queue(self, queue: Optional[asyncio.Queue]) -> None:
        """
        Set the output queue for this stage.

        Args:
            queue: Output queue to send data to, or None if this is the last stage
        """
        # Subclasses should override this if they need output queues
        pass


class PipelineCoordinator(ABC):
    """
    Abstract base class for coordinating pipeline stages.
    
    Responsible for connecting stages and managing the overall pipeline.
    """

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the pipeline coordinator.

        Args:
            config: Configuration dictionary for the entire pipeline

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass

    @abstractmethod
    async def start_pipeline(self) -> bool:
        """
        Start all pipeline stages.

        Returns:
            bool: True if pipeline started successfully, False otherwise
        """
        pass

    @abstractmethod
    async def stop_pipeline(self) -> None:
        """
        Stop all pipeline stages.
        """
        pass

    @abstractmethod
    def is_pipeline_running(self) -> bool:
        """
        Check if the pipeline is currently running.

        Returns:
            bool: True if pipeline is running, False otherwise
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up all pipeline resources.
        """
        pass