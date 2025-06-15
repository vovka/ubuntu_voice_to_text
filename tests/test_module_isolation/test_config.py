"""
Unit tests for Config class.

Tests the configuration management functionality in isolation.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def test_config_with_provided_dict():
    """Test Config initialization with provided configuration dictionary."""
    from voice_typing.config import Config
    
    # Test with custom configuration
    config_dict = {
        "model_path": "/test/model/path",
        "sample_rate": 22050,
        "recognition_source": "whisper",
        "openai_api_key": "test-api-key",
        "whisper_model": "custom-model",
        "hotkey_combo": {"ctrl", "shift", "space"}
    }
    
    config = Config(config_dict)
    
    # Verify all properties are set correctly
    assert config.MODEL_PATH == "/test/model/path"
    assert config.SAMPLE_RATE == 22050
    assert config.RECOGNITION_SOURCE == "whisper"
    assert config.OPENAI_API_KEY == "test-api-key"
    assert config.WHISPER_MODEL == "custom-model"
    assert config.HOTKEY_COMBO == {"ctrl", "shift", "space"}


def test_config_with_default_values():
    """Test Config initialization with default values."""
    from voice_typing.config import Config
    
    # Test with minimal configuration (should use defaults)
    config_dict = {
        "model_path": "/minimal/path"
    }
    
    config = Config(config_dict)
    
    # Verify defaults are applied
    assert config.MODEL_PATH == "/minimal/path"
    assert config.SAMPLE_RATE == 16000  # Default
    assert config.RECOGNITION_SOURCE == "vosk"  # Default
    assert config.OPENAI_API_KEY is None  # No default
    assert config.WHISPER_MODEL == "gpt-4o-transcribe"  # Default
    assert config.HOTKEY_COMBO == set()  # Default


def test_config_with_empty_dict():
    """Test Config initialization with empty dictionary."""
    from voice_typing.config import Config
    
    config = Config({})
    
    # Verify all defaults are applied
    assert config.MODEL_PATH is None
    assert config.SAMPLE_RATE == 16000
    assert config.RECOGNITION_SOURCE == "vosk"
    assert config.OPENAI_API_KEY is None
    assert config.WHISPER_MODEL == "gpt-4o-transcribe"
    assert config.HOTKEY_COMBO == set()


@patch('voice_typing.config.ConfigurationLoader')
def test_config_without_dict_uses_loader(mock_loader):
    """Test Config initialization without dict uses ConfigurationLoader."""
    from voice_typing.config import Config
    
    # Mock the configuration loader
    mock_loader.load_configuration.return_value = {
        "model_path": "/loaded/path",
        "sample_rate": 48000,
        "recognition_source": "loaded_source"
    }
    
    config = Config()  # No config_dict provided
    
    # Verify loader was called
    mock_loader.load_configuration.assert_called_once()
    
    # Verify loaded values are used
    assert config.MODEL_PATH == "/loaded/path"
    assert config.SAMPLE_RATE == 48000
    assert config.RECOGNITION_SOURCE == "loaded_source"


def test_config_properties_are_immutable():
    """Test that config properties cannot be modified after initialization."""
    from voice_typing.config import Config
    
    config_dict = {
        "model_path": "/original/path",
        "sample_rate": 16000
    }
    
    config = Config(config_dict)
    
    # Properties should not have setters
    with pytest.raises(AttributeError):
        config.MODEL_PATH = "/new/path"
    
    with pytest.raises(AttributeError):
        config.SAMPLE_RATE = 22050


def test_config_handles_none_values():
    """Test Config handles None values in configuration dictionary."""
    from voice_typing.config import Config
    
    config_dict = {
        "model_path": None,
        "sample_rate": None,
        "recognition_source": None,
        "openai_api_key": None,
        "whisper_model": None,
        "hotkey_combo": None
    }
    
    config = Config(config_dict)
    
    # Verify None values are preserved (dict.get returns None when value is None)
    assert config.MODEL_PATH is None
    assert config.SAMPLE_RATE is None  # None value is preserved, not replaced with default
    assert config.RECOGNITION_SOURCE is None  # None value is preserved
    assert config.OPENAI_API_KEY is None
    assert config.WHISPER_MODEL is None  # None value is preserved
    assert config.HOTKEY_COMBO is None  # None value is preserved


def test_config_defaults_for_missing_keys():
    """Test Config applies defaults for missing keys (vs None values)."""
    from voice_typing.config import Config
    
    # Empty dict - all keys missing
    config = Config({})
    
    # Verify defaults are applied for missing keys
    assert config.MODEL_PATH is None  # No default for model_path
    assert config.SAMPLE_RATE == 16000  # Default applied
    assert config.RECOGNITION_SOURCE == "vosk"  # Default applied
    assert config.OPENAI_API_KEY is None  # No default
    assert config.WHISPER_MODEL == "gpt-4o-transcribe"  # Default applied
    assert config.HOTKEY_COMBO == set()  # Default applied


def test_config_type_consistency():
    """Test that Config maintains consistent types for properties."""
    from voice_typing.config import Config
    
    config_dict = {
        "model_path": "/test/path",
        "sample_rate": 16000,
        "recognition_source": "test",
        "openai_api_key": "key",
        "whisper_model": "model",
        "hotkey_combo": {"ctrl", "alt"}
    }
    
    config = Config(config_dict)
    
    # Verify types
    assert isinstance(config.MODEL_PATH, str) or config.MODEL_PATH is None
    assert isinstance(config.SAMPLE_RATE, int)
    assert isinstance(config.RECOGNITION_SOURCE, str)
    assert isinstance(config.OPENAI_API_KEY, str) or config.OPENAI_API_KEY is None
    assert isinstance(config.WHISPER_MODEL, str)
    assert isinstance(config.HOTKEY_COMBO, set)


if __name__ == "__main__":
    # Run tests manually if called directly
    test_config_with_provided_dict()
    test_config_with_default_values()
    test_config_with_empty_dict()
    test_config_handles_none_values()
    test_config_type_consistency()
    
    print("✅ All Config unit tests passed!")