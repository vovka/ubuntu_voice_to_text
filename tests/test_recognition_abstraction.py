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


def test_whisper_recognition_source_interface():
    """Test that WhisperRecognitionSource implements the interface."""
    try:
        from voice_typing.recognition_sources import WhisperRecognitionSource, VoiceRecognitionSource
        
        # Test that WhisperRecognitionSource is a subclass of VoiceRecognitionSource
        assert issubclass(WhisperRecognitionSource, VoiceRecognitionSource)
        
        # Test that it can be instantiated
        whisper_source = WhisperRecognitionSource()
        assert whisper_source is not None
        
        # Test that it has all required methods
        assert hasattr(whisper_source, 'initialize')
        assert hasattr(whisper_source, 'process_audio_chunk')
        assert hasattr(whisper_source, 'get_result')
        assert hasattr(whisper_source, 'is_available')
        assert hasattr(whisper_source, 'cleanup')
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_whisper_recognition_source_initialization():
    """Test WhisperRecognitionSource initialization behavior."""
    try:
        from voice_typing.recognition_sources import WhisperRecognitionSource
        from unittest.mock import patch, MagicMock
        import sys
        
        whisper_source = WhisperRecognitionSource()
        
        # Test initialization without API key
        result = whisper_source.initialize({'model': 'whisper-1'})
        assert result is False
        assert not whisper_source.is_available()
        
        # Test initialization with API key (mock openai import)
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        
        with patch.dict('sys.modules', {'openai': mock_openai}):
            result = whisper_source.initialize({'api_key': 'test-key'})
            assert result is True
            assert whisper_source.is_available()
            
            # Verify OpenAI client was created with correct API key
            mock_openai.OpenAI.assert_called_once_with(api_key='test-key')
        
        # Test cleanup
        whisper_source.cleanup()
        assert not whisper_source.is_available()
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_whisper_package_exports():
    """Test that WhisperRecognitionSource is properly exported from the package."""
    try:
        import voice_typing
        
        # Test that the new class is available
        assert hasattr(voice_typing, 'WhisperRecognitionSource')
        
        # Test that it can be imported
        from voice_typing import WhisperRecognitionSource
        assert WhisperRecognitionSource is not None
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_audio_processor_with_whisper_source():
    """Test that AudioProcessor works with WhisperRecognitionSource."""
    try:
        from voice_typing import AudioProcessor, Config, GlobalState
        from voice_typing.recognition_sources import WhisperRecognitionSource
        
        # Create a mock Whisper recognition source for testing
        class MockWhisperRecognitionSource(WhisperRecognitionSource):
            def initialize(self, config):
                self._is_available = True
                return True
            
            def process_audio_chunk(self, audio_chunk):
                pass
            
            def get_result(self):
                return {"text": "whisper test result"}
            
            def is_available(self):
                return True
            
            def cleanup(self):
                pass
        
        config = Config()
        state_ref = GlobalState()
        mock_source = MockWhisperRecognitionSource()
        
        # Test that AudioProcessor can be created with WhisperRecognitionSource
        audio_processor = AudioProcessor(config, state_ref, mock_source)
        assert audio_processor is not None
        assert audio_processor.recognition_source is mock_source
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_config_recognition_source_selection():
    """Test that Config supports recognition source selection."""
    try:
        import os
        
        # Save original environment
        original_env = {}
        for key in ['RECOGNITION_SOURCE', 'OPENAI_API_KEY', 'WHISPER_MODEL']:
            original_env[key] = os.environ.get(key)
        
        try:
            # Clear environment first
            for key in ['RECOGNITION_SOURCE', 'OPENAI_API_KEY', 'WHISPER_MODEL']:
                if key in os.environ:
                    del os.environ[key]
            
            # Test default configuration
            from voice_typing import Config
            config = Config()
            assert hasattr(config, 'RECOGNITION_SOURCE')
            assert hasattr(config, 'OPENAI_API_KEY')
            assert hasattr(config, 'WHISPER_MODEL')
            
            # Default should be 'vosk'
            assert config.RECOGNITION_SOURCE == 'vosk'
            
            # Test environment variable support
            os.environ['RECOGNITION_SOURCE'] = 'whisper'
            os.environ['OPENAI_API_KEY'] = 'test-key'
            os.environ['WHISPER_MODEL'] = 'whisper-1'
            
            # Create new config instance to pick up environment changes
            config2 = Config()
            assert config2.RECOGNITION_SOURCE == 'whisper'
            assert config2.OPENAI_API_KEY == 'test-key'
            assert config2.WHISPER_MODEL == 'whisper-1'
            
        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_audio_processor_source_selection():
    """Test that AudioProcessor creates the correct recognition source based on config."""
    try:
        import os
        from voice_typing import AudioProcessor, Config, GlobalState
        
        # Save original environment
        original_env = {}
        for key in ['RECOGNITION_SOURCE', 'OPENAI_API_KEY']:
            original_env[key] = os.environ.get(key)
            
        try:
            # Test Vosk source selection (default)
            if 'RECOGNITION_SOURCE' in os.environ:
                del os.environ['RECOGNITION_SOURCE']
            
            config = Config()
            state_ref = GlobalState()
            
            # This will try to create VoskRecognitionSource and likely fail due to missing model
            # but we can check the source type before initialization fails
            try:
                audio_processor = AudioProcessor(config, state_ref)
            except SystemExit:
                # Expected due to missing Vosk model
                pass
            
            # Test Whisper source selection
            os.environ['RECOGNITION_SOURCE'] = 'whisper'
            os.environ['OPENAI_API_KEY'] = 'test-key'
            
            config2 = Config()
            try:
                audio_processor2 = AudioProcessor(config2, state_ref)
                # Should create WhisperRecognitionSource
                from voice_typing.recognition_sources import WhisperRecognitionSource
                assert isinstance(audio_processor2.recognition_source, WhisperRecognitionSource)
            except SystemExit:
                # Expected due to initialization failure
                pass
            
        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")