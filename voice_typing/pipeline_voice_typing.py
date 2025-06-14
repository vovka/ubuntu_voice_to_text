"""
Pipeline-based Voice Typing implementation.

This module provides a new VoiceTyping class that uses the decoupled
audio pipeline architecture while maintaining compatibility with
the existing system.
"""

import asyncio
import threading
from typing import Optional, Dict, Any
from .config import Config
from .global_state import GlobalState
from .pipeline import AudioPipelineCoordinator, SoundDeviceAudioInput
from .recognition_sources import RecognitionSourceFactory, VoiceRecognitionSource
from .tray_icon_manager import TrayIconManager
from .interfaces.output_action import OutputDispatcher, KeyboardOutputActionTarget


class PipelineVoiceTyping:
    """
    Voice typing implementation using the decoupled audio pipeline.
    
    This provides a bridge between the existing system and the new
    pipeline architecture.
    """

    def __init__(
        self,
        config: Config,
        state_ref: GlobalState,
        tray_icon_manager: TrayIconManager,
        recognition_source: Optional[VoiceRecognitionSource] = None,
        output_dispatcher: Optional[OutputDispatcher] = None,
    ):
        self.config = config
        self.state_ref = state_ref
        self.tray_icon_manager = tray_icon_manager
        
        # Create audio input
        self.audio_input = SoundDeviceAudioInput()
        
        # Use provided recognition source or create from config
        if recognition_source is None:
            recognition_source = RecognitionSourceFactory.create_recognition_source(config)
        self.recognition_source = recognition_source
        
        # Set up output dispatcher
        if output_dispatcher is None:
            output_dispatcher = OutputDispatcher()
            output_dispatcher.initialize()
            
            # Add default keyboard output target
            keyboard_target = KeyboardOutputActionTarget()
            if keyboard_target.initialize({}):
                output_dispatcher.add_target(keyboard_target)
            else:
                print("[PipelineVoiceTyping] ⚠️ Warning: Keyboard output target not available")
        
        self.output_dispatcher = output_dispatcher
        
        # Pipeline coordinator
        self.pipeline_coordinator: Optional[AudioPipelineCoordinator] = None
        
        # Threading for async pipeline
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._pipeline_thread: Optional[threading.Thread] = None
        self._running = False

    def _text_output_callback(self, text: str) -> None:
        """Handle recognized text output."""
        print(f"[PipelineVoiceTyping] 🗣️ {text}")
        
        # Dispatch text through output dispatcher
        import time
        metadata = {
            'confidence': 1.0,  # Pipeline doesn't provide confidence yet
            'timestamp': time.time(),
            'source': 'PipelineVoiceTyping'
        }
        self.output_dispatcher.dispatch_text(text, metadata)

    def _setup_pipeline(self) -> bool:
        """Set up the audio pipeline coordinator."""
        self.pipeline_coordinator = AudioPipelineCoordinator(
            self.audio_input,
            self.recognition_source,
            self._text_output_callback
        )
        return True

    def _pipeline_thread_func(self) -> None:
        """Run the async pipeline in a separate thread."""
        # Create new event loop for this thread
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        try:
            self._loop.run_until_complete(self._run_pipeline())
        except Exception as e:
            print(f"[PipelineVoiceTyping] Pipeline thread error: {e}")
        finally:
            self._loop.close()

    async def _run_pipeline(self) -> None:
        """Main async pipeline execution."""
        if not self.pipeline_coordinator:
            return
            
        # Initialize pipeline
        pipeline_config = {
            'sample_rate': self.config.SAMPLE_RATE,
            'channels': 1,
            'block_size': 8000,
            'dtype': 'int16',
            'buffer_size': 10,
            'queue_size': 100,
        }
        
        # Add recognition config
        recognition_config = RecognitionSourceFactory.get_recognition_config(self.config)
        pipeline_config.update(recognition_config)
        
        if not await self.pipeline_coordinator.initialize(pipeline_config):
            print("[PipelineVoiceTyping] Failed to initialize pipeline")
            return
        
        try:
            while self._running:
                current_state = self.state_ref.state
                
                if current_state in ("listening", "finish_listening"):
                    if not self.pipeline_coordinator.is_pipeline_running():
                        print("[PipelineVoiceTyping] Starting pipeline for listening state")
                        await self.pipeline_coordinator.start_pipeline()
                else:
                    if self.pipeline_coordinator.is_pipeline_running():
                        print("[PipelineVoiceTyping] Stopping pipeline for idle state")
                        await self.pipeline_coordinator.stop_pipeline()
                
                # Check periodically
                await asyncio.sleep(0.1)
                
        finally:
            await self.pipeline_coordinator.stop_pipeline()
            await self.pipeline_coordinator.cleanup()

    def start_pipeline_system(self) -> bool:
        """Start the pipeline-based voice typing system."""
        if self._running:
            return True
            
        if not self._setup_pipeline():
            return False
        
        self._running = True
        self._pipeline_thread = threading.Thread(
            target=self._pipeline_thread_func,
            daemon=True
        )
        self._pipeline_thread.start()
        return True

    def stop_pipeline_system(self) -> None:
        """Stop the pipeline-based voice typing system."""
        if not self._running:
            return
            
        self._running = False
        
        if self._pipeline_thread and self._pipeline_thread.is_alive():
            self._pipeline_thread.join(timeout=5.0)

    def voice_typing_loop(self) -> None:
        """Main voice typing loop with pipeline integration."""
        print("[PipelineVoiceTyping] Starting pipeline-based voice typing system")
        
        if not self.start_pipeline_system():
            print("[PipelineVoiceTyping] Failed to start pipeline system")
            return
        
        try:
            print(
                "[PipelineVoiceTyping] 🎤 Voice typing ready. Press and release "
                "Ctrl+Shift to start listening."
            )
            
            # Main loop just monitors state and updates tray icon
            while True:
                try:
                    # Update tray icon
                    self.tray_icon_manager.update_icon()
                    
                    # Small delay to prevent busy waiting
                    import time
                    time.sleep(0.1)
                    
                except KeyboardInterrupt:
                    print("[PipelineVoiceTyping] Keyboard interrupt received")
                    break
                except Exception as e:
                    print(f"[PipelineVoiceTyping] Error in main loop: {e}")
                    
        finally:
            print("[PipelineVoiceTyping] Shutting down pipeline system")
            self.stop_pipeline_system()

    # Backward compatibility methods
    def audio_callback(self, indata, frames, time, status):
        """Legacy audio callback - not used in pipeline mode."""
        # This method exists for backward compatibility but is not used
        # in the pipeline-based implementation
        pass