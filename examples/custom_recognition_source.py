"""
Example demonstrating how to use the voice recognition abstraction layer.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_typing.recognition_sources import VoiceRecognitionSource


class MockRecognitionSource(VoiceRecognitionSource):
    """Example mock recognition source for testing or demonstration."""

    def __init__(self):
        self._initialized = False
        self._counter = 0

    def initialize(self, config):
        """Initialize the mock source."""
        print(f"[MockRecognitionSource] Initializing with config: {config}")
        self._initialized = True
        return True

    def process_audio_chunk(self, audio_chunk):
        """Process audio chunk (mock implementation)."""
        self._counter += 1
        print(f"[MockRecognitionSource] Processed chunk #{self._counter}")

    def get_result(self):
        """Return a mock result every 3 chunks."""
        if self._counter % 3 == 0:
            return {"text": f"mock result {self._counter // 3}"}
        return None

    def is_available(self):
        """Check if the source is available."""
        return self._initialized

    def cleanup(self):
        """Clean up resources."""
        print("[MockRecognitionSource] Cleaning up...")
        self._initialized = False


def example_usage():
    """Example of how to use a custom recognition source."""
    from voice_typing import AudioProcessor, Config, GlobalState

    # Create configuration and state
    config = Config()
    state_ref = GlobalState()

    # Create custom recognition source
    mock_source = MockRecognitionSource()

    # Create AudioProcessor with custom source
    try:
        audio_processor = AudioProcessor(config, state_ref, mock_source)
        print("✅ AudioProcessor created successfully with custom source!")

        # Simulate processing some audio chunks
        mock_audio_chunks = [b"chunk1", b"chunk2", b"chunk3"]
        for chunk in mock_audio_chunks:
            audio_processor.recognition_source.process_audio_chunk(chunk)
            result = audio_processor.recognition_source.get_result()
            if result:
                print(f"Got result: {result}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    example_usage()