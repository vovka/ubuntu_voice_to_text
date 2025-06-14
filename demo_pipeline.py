#!/usr/bin/env python3
"""
Demo script showing the decoupled audio pipeline in action.

This demonstrates how the pipeline stages can be used independently
and how they communicate via queues.
"""

import asyncio
import time
from typing import Dict, Any, Optional

from voice_typing.pipeline import (
    AudioPipelineCoordinator,
    SoundDeviceAudioInput,
    AudioCaptureStage,
    AudioBufferingStage,
    RecognitionStage,
)
from voice_typing.recognition_sources import VoiceRecognitionSource


class DemoRecognitionSource(VoiceRecognitionSource):
    """Demo recognition source that simulates speech recognition."""
    
    def __init__(self):
        self._initialized = False
        self._chunk_count = 0
        self._results = []
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        print("[DemoRecognitionSource] Initializing...")
        self._initialized = True
        return True
    
    def process_audio_chunk(self, audio_chunk: bytes) -> None:
        if self._initialized:
            self._chunk_count += 1
            print(f"[DemoRecognitionSource] Processed chunk {self._chunk_count} ({len(audio_chunk)} bytes)")
            
            # Simulate recognition after several chunks
            if self._chunk_count % 5 == 0:
                text = f"recognized_text_batch_{self._chunk_count // 5}"
                self._results.append({
                    'text': text,
                    'confidence': 0.9,
                    'final': True
                })
                print(f"[DemoRecognitionSource] Generated result: {text}")
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        if self._results:
            result = self._results.pop(0)
            print(f"[DemoRecognitionSource] Returning result: {result}")
            return result
        return None
    
    def is_available(self) -> bool:
        return self._initialized
    
    def cleanup(self) -> None:
        print("[DemoRecognitionSource] Cleaning up...")
        self._initialized = False
        self._chunk_count = 0
        self._results.clear()


class MockAudioInput(SoundDeviceAudioInput):
    """Mock audio input that generates test data instead of capturing real audio."""
    
    def __init__(self):
        super().__init__()
        self._demo_mode = True
        self._chunk_generator = None
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        print("[MockAudioInput] Initializing in demo mode...")
        self._config = config
        return True
    
    def start_capture(self, callback) -> bool:
        print("[MockAudioInput] Starting demo audio capture...")
        self._callback = callback
        
        # Start generating demo audio chunks
        asyncio.create_task(self._generate_demo_audio())
        return True
    
    async def _generate_demo_audio(self):
        """Generate demo audio chunks."""
        chunk_size = self._config.get('block_size', 8000)
        for i in range(20):  # Generate 20 chunks
            if not self._callback:
                break
                
            # Generate dummy audio data
            audio_chunk = bytes([i % 256] * chunk_size)
            print(f"[MockAudioInput] Generated audio chunk {i+1}")
            self._callback(audio_chunk)
            
            # Wait between chunks
            await asyncio.sleep(0.5)
        
        print("[MockAudioInput] Demo audio generation complete")
    
    def is_available(self) -> bool:
        return True
    
    def is_capturing(self) -> bool:
        return self._callback is not None


async def demo_individual_stages():
    """Demonstrate individual pipeline stages working in isolation."""
    print("\n=== Demo: Individual Pipeline Stages ===")
    
    # Create mock components
    audio_input = MockAudioInput()
    recognition_source = DemoRecognitionSource()
    
    recognized_texts = []
    def text_callback(text: str):
        recognized_texts.append(text)
        print(f"[Demo] Recognized text: '{text}'")
    
    # Demo audio capture stage
    print("\n--- Audio Capture Stage ---")
    capture_stage = AudioCaptureStage(audio_input)
    output_queue = asyncio.Queue()
    capture_stage.set_output_queue(output_queue)
    
    config = {'sample_rate': 16000, 'block_size': 8000, 'channels': 1}
    await capture_stage.initialize(config)
    await capture_stage.start()
    
    # Let it capture a few chunks
    await asyncio.sleep(2.0)
    await capture_stage.stop()
    
    # Check captured chunks
    captured_chunks = []
    while not output_queue.empty():
        captured_chunks.append(await output_queue.get())
    
    print(f"[Demo] Captured {len(captured_chunks)} audio chunks")
    
    # Demo buffering stage
    print("\n--- Audio Buffering Stage ---")
    buffering_stage = AudioBufferingStage(buffer_size=3)
    input_queue = asyncio.Queue()
    buffer_output_queue = asyncio.Queue()
    
    buffering_stage.set_input_queue(input_queue)
    buffering_stage.set_output_queue(buffer_output_queue)
    
    await buffering_stage.initialize({'buffer_size': 3})
    await buffering_stage.start()
    
    # Feed captured chunks to buffering stage
    for chunk in captured_chunks[:6]:  # Use first 6 chunks
        await input_queue.put(chunk)
    
    await asyncio.sleep(1.0)
    await buffering_stage.stop()
    
    # Check buffered results
    buffers = []
    while not buffer_output_queue.empty():
        buffers.append(await buffer_output_queue.get())
    
    print(f"[Demo] Created {len(buffers)} buffers")
    
    # Demo recognition stage
    print("\n--- Recognition Stage ---")
    recognition_stage = RecognitionStage(recognition_source, text_callback)
    recognition_input_queue = asyncio.Queue()
    recognition_stage.set_input_queue(recognition_input_queue)
    
    await recognition_stage.initialize(config)
    await recognition_stage.start()
    
    # Feed buffers to recognition stage
    for buffer in buffers:
        await recognition_input_queue.put(buffer)
    
    await asyncio.sleep(2.0)
    await recognition_stage.stop()
    
    print(f"[Demo] Recognized {len(recognized_texts)} texts: {recognized_texts}")
    
    # Cleanup
    await capture_stage.cleanup()
    await buffering_stage.cleanup()
    await recognition_stage.cleanup()


async def demo_full_pipeline():
    """Demonstrate the full pipeline coordinator."""
    print("\n=== Demo: Full Pipeline Coordinator ===")
    
    audio_input = MockAudioInput()
    recognition_source = DemoRecognitionSource()
    
    recognized_texts = []
    def text_callback(text: str):
        recognized_texts.append(text)
        print(f"[Demo] Pipeline recognized: '{text}'")
    
    # Create pipeline coordinator
    coordinator = AudioPipelineCoordinator(
        audio_input,
        recognition_source,
        text_callback
    )
    
    # Initialize and start pipeline
    config = {
        'sample_rate': 16000,
        'channels': 1,
        'block_size': 8000,
        'buffer_size': 3,
        'queue_size': 50
    }
    
    print("[Demo] Initializing pipeline...")
    await coordinator.initialize(config)
    
    print("[Demo] Starting pipeline...")
    await coordinator.start_pipeline()
    
    # Check pipeline status
    status = coordinator.get_stage_status()
    print(f"[Demo] Pipeline status: {status}")
    
    # Let pipeline run for a while
    print("[Demo] Pipeline running for 10 seconds...")
    await asyncio.sleep(10.0)
    
    print("[Demo] Stopping pipeline...")
    await coordinator.stop_pipeline()
    
    print(f"[Demo] Final results: {len(recognized_texts)} texts recognized")
    for i, text in enumerate(recognized_texts):
        print(f"  {i+1}. {text}")
    
    # Cleanup
    await coordinator.cleanup()


async def main():
    """Run the full demo."""
    print("Audio Pipeline Decoupling Demo")
    print("=" * 40)
    
    try:
        await demo_individual_stages()
        await demo_full_pipeline()
        
        print("\n🎉 Demo completed successfully!")
        print("\nThe audio pipeline demonstrates:")
        print("- Modular stages that can be tested in isolation")
        print("- Queue-based communication between stages")
        print("- Clean separation of concerns")
        print("- Easy integration with existing interfaces")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())