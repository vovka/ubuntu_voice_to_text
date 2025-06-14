"""
Pipeline stages for audio processing.

Implements the individual stages of the audio pipeline using
the existing interfaces.
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable
from .interfaces import AudioPipelineStage
from ..interfaces import AudioInputSource, VoiceRecognitionSource


class AudioCaptureStage(AudioPipelineStage):
    """
    Pipeline stage that captures audio data using an AudioInputSource.
    """

    def __init__(self, audio_input: AudioInputSource):
        """
        Initialize with an AudioInputSource implementation.

        Args:
            audio_input: The audio input source to use for capture
        """
        self._audio_input = audio_input
        self._output_queue: Optional[asyncio.Queue] = None
        self._input_queue: Optional[asyncio.Queue] = None  # Not used but needed for interface
        self._running = False
        self._config: Optional[Dict[str, Any]] = None

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the audio capture stage."""
        self._config = config
        return self._audio_input.initialize(config)

    async def start(self) -> bool:
        """Start audio capture."""
        if self._running:
            return True

        if not self._audio_input.is_available():
            return False

        def audio_callback(audio_chunk: bytes) -> None:
            """Callback to receive audio chunks and put them in the output queue."""
            if self._output_queue and self._running:
                try:
                    # Use asyncio.run_coroutine_threadsafe to safely put from callback thread
                    if self._event_loop:
                        asyncio.run_coroutine_threadsafe(
                            self._output_queue.put(audio_chunk), self._event_loop
                        )
                except Exception as e:
                    print(f"[AudioCaptureStage] Error putting audio chunk: {e}")

        self._event_loop = asyncio.get_running_loop()
        if self._audio_input.start_capture(audio_callback):
            self._running = True
            return True
        
        return False

    async def stop(self) -> None:
        """Stop audio capture."""
        if self._running:
            self._running = False
            self._audio_input.stop_capture()

    def is_running(self) -> bool:
        """Check if capture is running."""
        return self._running and self._audio_input.is_capturing()

    async def cleanup(self) -> None:
        """Clean up audio capture resources."""
        await self.stop()
        self._audio_input.cleanup()

    def set_output_queue(self, queue: Optional[asyncio.Queue]) -> None:
        """Set the output queue for this stage."""
        self._output_queue = queue


class AudioBufferingStage(AudioPipelineStage):
    """
    Pipeline stage that buffers audio chunks before processing.
    """

    def __init__(self, buffer_size: int = 10):
        """
        Initialize the buffering stage.

        Args:
            buffer_size: Maximum number of audio chunks to buffer
        """
        self._buffer_size = buffer_size
        self._input_queue: Optional[asyncio.Queue] = None
        self._output_queue: Optional[asyncio.Queue] = None
        self._running = False
        self._buffer = []
        self._task: Optional[asyncio.Task] = None

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the buffering stage."""
        # Get buffer size from config if provided
        self._buffer_size = config.get('buffer_size', self._buffer_size)
        return True

    async def start(self) -> bool:
        """Start the buffering process."""
        if self._running:
            return True

        if not self._input_queue or not self._output_queue:
            return False

        self._running = True
        self._task = asyncio.create_task(self._buffering_loop())
        return True

    async def _buffering_loop(self) -> None:
        """Main buffering loop that processes chunks."""
        while self._running:
            try:
                # Get audio chunk from input queue
                audio_chunk = await asyncio.wait_for(
                    self._input_queue.get(), timeout=0.1
                )
                
                # Add to buffer
                self._buffer.append(audio_chunk)
                
                # Send buffer when it reaches size limit or on timeout
                if len(self._buffer) >= self._buffer_size:
                    await self._flush_buffer()
                    
            except asyncio.TimeoutError:
                # Flush buffer periodically even if not full
                if self._buffer:
                    await self._flush_buffer()
            except Exception as e:
                print(f"[AudioBufferingStage] Error in buffering loop: {e}")

    async def _flush_buffer(self) -> None:
        """Send the current buffer to the output queue."""
        if self._buffer and self._output_queue:
            buffer_copy = self._buffer.copy()
            self._buffer.clear()
            await self._output_queue.put(buffer_copy)

    async def stop(self) -> None:
        """Stop the buffering process."""
        self._running = False
        if self._task:
            await self._task
            self._task = None

    def is_running(self) -> bool:
        """Check if buffering is running."""
        return self._running

    async def cleanup(self) -> None:
        """Clean up buffering resources."""
        await self.stop()
        self._buffer.clear()

    def set_input_queue(self, queue: Optional[asyncio.Queue]) -> None:
        """Set the input queue for this stage."""
        self._input_queue = queue

    def set_output_queue(self, queue: Optional[asyncio.Queue]) -> None:
        """Set the output queue for this stage."""
        self._output_queue = queue


class RecognitionStage(AudioPipelineStage):
    """
    Pipeline stage that performs voice recognition on audio buffers.
    """

    def __init__(self, recognition_source: VoiceRecognitionSource, output_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize with a VoiceRecognitionSource implementation.

        Args:
            recognition_source: The recognition source to use
            output_callback: Optional callback to handle recognized text
        """
        self._recognition_source = recognition_source
        self._output_callback = output_callback
        self._input_queue: Optional[asyncio.Queue] = None
        self._output_queue: Optional[asyncio.Queue] = None  # Not used but needed for interface
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the recognition stage."""
        return self._recognition_source.initialize(config)

    async def start(self) -> bool:
        """Start the recognition process."""
        if self._running:
            return True

        if not self._input_queue:
            return False

        if not self._recognition_source.is_available():
            return False

        self._running = True
        self._task = asyncio.create_task(self._recognition_loop())
        return True

    async def _recognition_loop(self) -> None:
        """Main recognition loop that processes audio buffers."""
        while self._running:
            try:
                # Get audio buffer from input queue
                audio_buffer = await asyncio.wait_for(
                    self._input_queue.get(), timeout=0.1
                )
                
                # Process each chunk in the buffer
                for audio_chunk in audio_buffer:
                    self._recognition_source.process_audio_chunk(audio_chunk)
                
                # Check for recognition results
                result = self._recognition_source.get_result()
                if result and result.get("text") and self._output_callback:
                    self._output_callback(result["text"])
                    
            except asyncio.TimeoutError:
                # Check for results even without new audio
                result = self._recognition_source.get_result()
                if result and result.get("text") and self._output_callback:
                    self._output_callback(result["text"])
            except Exception as e:
                print(f"[RecognitionStage] Error in recognition loop: {e}")

    async def stop(self) -> None:
        """Stop the recognition process."""
        self._running = False
        if self._task:
            await self._task
            self._task = None

    def is_running(self) -> bool:
        """Check if recognition is running."""
        return self._running

    async def cleanup(self) -> None:
        """Clean up recognition resources."""
        await self.stop()
        self._recognition_source.cleanup()

    def set_input_queue(self, queue: Optional[asyncio.Queue]) -> None:
        """Set the input queue for this stage."""
        self._input_queue = queue