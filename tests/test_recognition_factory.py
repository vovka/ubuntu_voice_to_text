"""
Tests for Recognition Source Factory pattern.
"""

import sys
import os
import pytest

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_recognition_source_factory_import():
    """Test that RecognitionSourceFactory can be imported."""
    try:
        from voice_typing.recognition_sources import RecognitionSourceFactory
        assert RecognitionSourceFactory is not None
        
        # Test factory methods exist
        assert hasattr(RecognitionSourceFactory, 'create_recognition_source')
        assert hasattr(RecognitionSourceFactory, 'get_recognition_config')
        assert hasattr(RecognitionSourceFactory, 'get_available_sources')
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_factory_create_vosk_source():
    """Test factory creates VoskRecognitionSource for vosk config."""
    try:
        from voice_typing import Config, RecognitionSourceFactory
        from voice_typing.recognition_sources import VoskRecognitionSource
        
        # Create config with vosk source
        config = Config()
        # Mock the recognition source to be vosk
        original_get = os.environ.get
        os.environ.get = lambda key, default=None: 'vosk' if key == 'RECOGNITION_SOURCE' else original_get(key, default)
        
        try:
            source = RecognitionSourceFactory.create_recognition_source(config)
            assert isinstance(source, VoskRecognitionSource)
        finally:
            os.environ.get = original_get
            
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_factory_create_whisper_source():
    """Test factory creates WhisperRecognitionSource for whisper config."""
    try:
        from voice_typing import Config, RecognitionSourceFactory
        from voice_typing.recognition_sources import WhisperRecognitionSource
        
        # Save original environment
        original_env = os.environ.get("RECOGNITION_SOURCE")
        
        try:
            # Set environment for whisper
            os.environ["RECOGNITION_SOURCE"] = "whisper"
            
            config = Config()
            source = RecognitionSourceFactory.create_recognition_source(config)
            assert isinstance(source, WhisperRecognitionSource)
            
        finally:
            # Restore environment
            if original_env is not None:
                os.environ["RECOGNITION_SOURCE"] = original_env
            elif "RECOGNITION_SOURCE" in os.environ:
                del os.environ["RECOGNITION_SOURCE"]
            
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_factory_create_unknown_source_defaults_to_vosk():
    """Test factory defaults to VoskRecognitionSource for unknown source types."""
    try:
        from voice_typing import Config, RecognitionSourceFactory
        from voice_typing.recognition_sources import VoskRecognitionSource
        
        # Save original environment
        original_env = os.environ.get("RECOGNITION_SOURCE")
        
        try:
            # Set environment for unknown source
            os.environ["RECOGNITION_SOURCE"] = "unknown_source"
            
            config = Config()
            source = RecognitionSourceFactory.create_recognition_source(config)
            assert isinstance(source, VoskRecognitionSource)
            
        finally:
            # Restore environment
            if original_env is not None:
                os.environ["RECOGNITION_SOURCE"] = original_env
            elif "RECOGNITION_SOURCE" in os.environ:
                del os.environ["RECOGNITION_SOURCE"]
            
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_factory_get_vosk_config():
    """Test factory generates correct config for Vosk source."""
    try:
        from voice_typing import Config, RecognitionSourceFactory
        
        # Save original environment
        original_env = os.environ.get("RECOGNITION_SOURCE")
        
        try:
            # Set environment for vosk
            if "RECOGNITION_SOURCE" in os.environ:
                del os.environ["RECOGNITION_SOURCE"]  # Use default (vosk)
            
            config = Config()
            recognition_config = RecognitionSourceFactory.get_recognition_config(config)
            
            assert "sample_rate" in recognition_config
            assert recognition_config["sample_rate"] == config.SAMPLE_RATE
            assert "model_path" in recognition_config
            assert recognition_config["model_path"] == config.MODEL_PATH
            
            # Should not have whisper-specific keys
            assert "api_key" not in recognition_config
            assert "model" not in recognition_config
            
        finally:
            # Restore environment
            if original_env is not None:
                os.environ["RECOGNITION_SOURCE"] = original_env
            
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_factory_get_whisper_config():
    """Test factory generates correct config for Whisper source."""
    try:
        from voice_typing import Config, RecognitionSourceFactory
        
        # Save original environment
        original_env = {}
        for key in ["RECOGNITION_SOURCE", "OPENAI_API_KEY", "WHISPER_MODEL"]:
            original_env[key] = os.environ.get(key)
        
        try:
            # Set environment for whisper
            os.environ["RECOGNITION_SOURCE"] = "whisper"
            os.environ["OPENAI_API_KEY"] = "test-api-key"
            os.environ["WHISPER_MODEL"] = "test-model"
            
            config = Config()
            recognition_config = RecognitionSourceFactory.get_recognition_config(config)
            
            assert "sample_rate" in recognition_config
            assert recognition_config["sample_rate"] == config.SAMPLE_RATE
            assert "api_key" in recognition_config
            assert recognition_config["api_key"] == "test-api-key"
            assert "model" in recognition_config
            assert recognition_config["model"] == "test-model"
            
            # Should not have vosk-specific keys
            assert "model_path" not in recognition_config
            
        finally:
            # Restore environment
            for key, value in original_env.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
            
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_factory_get_available_sources():
    """Test factory returns correct list of available sources."""
    try:
        from voice_typing import RecognitionSourceFactory
        
        available_sources = RecognitionSourceFactory.get_available_sources()
        
        assert isinstance(available_sources, list)
        assert "vosk" in available_sources
        assert "whisper" in available_sources
        assert len(available_sources) == 2
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_factory_isolation_and_testability():
    """Test that factory is isolated and testable independently."""
    try:
        from voice_typing import RecognitionSourceFactory
        
        # Test that factory can be used without AudioProcessor
        assert RecognitionSourceFactory.get_available_sources() == ["vosk", "whisper"]
        
        # Test that factory methods are static methods (callable without instance)
        assert callable(RecognitionSourceFactory.create_recognition_source)
        assert callable(RecognitionSourceFactory.get_recognition_config)
        assert callable(RecognitionSourceFactory.get_available_sources)
        
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")


def test_audio_processor_uses_factory():
    """Test that AudioProcessor uses factory instead of direct instantiation."""
    try:
        from voice_typing import AudioProcessor, Config, GlobalState
        from voice_typing.recognition_sources import VoskRecognitionSource
        
        # Create a mock to verify factory is called
        import unittest.mock
        
        with unittest.mock.patch('voice_typing.recognition_sources.RecognitionSourceFactory.create_recognition_source') as mock_create:
            mock_create.return_value = VoskRecognitionSource()
            
            with unittest.mock.patch('voice_typing.recognition_sources.RecognitionSourceFactory.get_recognition_config') as mock_config:
                mock_config.return_value = {"sample_rate": 16000, "model_path": "/fake/path"}
                
                config = Config()
                state_ref = GlobalState()
                
                # Mock the recognition source initialization to avoid actual file access
                with unittest.mock.patch.object(VoskRecognitionSource, 'initialize', return_value=True):
                    AudioProcessor(config, state_ref)
                    
                    # Verify factory methods were called
                    mock_create.assert_called_once_with(config)
                    mock_config.assert_called_once_with(config)
            
    except ImportError as e:
        pytest.skip(f"Skipping due to missing dependencies: {e}")