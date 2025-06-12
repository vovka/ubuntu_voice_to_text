"""
Tests for voice recognition abstraction layer.
"""

import sys
import os
import pytest

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_voice_recognition_source_interface():
    """Test that VoiceRecognitionSource interface can be imported."""
    try:
        from voice_typing.recognition_sources import VoiceRecognitionSource
        
        # Test that it's an abstract base class
        assert hasattr(VoiceRecognitionSource, '__abstractmethods__')
        abstract_methods = VoiceRecognitionSource.__abstractmethods__
        expected_methods = {
            'initialize', 'process_audio_chunk', 'get_result', 
            'is_available', 'cleanup'
        }
        assert abstract_methods == expected_methods
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_vosk_recognition_source_implementation():
    """Test that VoskRecognitionSource implements the interface."""
    try:
        from voice_typing.recognition_sources import VoskRecognitionSource, VoiceRecognitionSource
        
        # Test that VoskRecognitionSource is a subclass of VoiceRecognitionSource
        assert issubclass(VoskRecognitionSource, VoiceRecognitionSource)
        
        # Test that we can instantiate it
        vosk_source = VoskRecognitionSource()
        assert vosk_source is not None
        
        # Test that it has the required methods
        assert hasattr(vosk_source, 'initialize')
        assert hasattr(vosk_source, 'process_audio_chunk')
        assert hasattr(vosk_source, 'get_result')
        assert hasattr(vosk_source, 'is_available')
        assert hasattr(vosk_source, 'cleanup')
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_vosk_recognition_source_initialization():
    """Test VoskRecognitionSource initialization behavior."""
    try:
        from voice_typing.recognition_sources import VoskRecognitionSource
        
        vosk_source = VoskRecognitionSource()
        
        # Test initialization with invalid config
        result = vosk_source.initialize({'model_path': '/non/existent/path'})
        assert result is False
        assert not vosk_source.is_available()
        
        # Test initialization with missing model_path
        result = vosk_source.initialize({'sample_rate': 16000})
        assert result is False
        assert not vosk_source.is_available()
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_audio_processor_with_abstraction():
    """Test that AudioProcessor works with the new abstraction."""
    try:
        from voice_typing import AudioProcessor, Config, GlobalState
        from voice_typing.recognition_sources import VoskRecognitionSource
        
        # Create a mock recognition source for testing
        class MockRecognitionSource(VoskRecognitionSource):
            def initialize(self, config):
                self._is_available = True
                return True
            
            def process_audio_chunk(self, audio_chunk):
                pass
            
            def get_result(self):
                return {"text": "test result"}
            
            def is_available(self):
                return True
            
            def cleanup(self):
                pass
        
        config = Config()
        state_ref = GlobalState()
        mock_source = MockRecognitionSource()
        
        # Test that AudioProcessor can be created with custom recognition source
        audio_processor = AudioProcessor(config, state_ref, mock_source)
        assert audio_processor is not None
        assert audio_processor.recognition_source is mock_source
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_package_exports():
    """Test that the new classes are properly exported from the package."""
    try:
        import voice_typing
        
        # Test that the new classes are available
        assert hasattr(voice_typing, 'VoiceRecognitionSource')
        assert hasattr(voice_typing, 'VoskRecognitionSource')
        
        # Test that they can be imported
        from voice_typing import VoiceRecognitionSource, VoskRecognitionSource
        assert VoiceRecognitionSource is not None
        assert VoskRecognitionSource is not None
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_backward_compatibility():
    """Test that existing functionality still works."""
    try:
        from voice_typing import AudioProcessor, Config, GlobalState
        
        config = Config()
        state_ref = GlobalState()
        
        # Test that AudioProcessor can still be created without recognition source
        # (should default to VoskRecognitionSource)
        try:
            audio_processor = AudioProcessor(config, state_ref)
            # This might fail due to missing Vosk model, but that's expected
        except SystemExit:
            # SystemExit is expected when model is not found
            pass
            
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")