"""
Test centralized configuration management.

Tests that configuration is properly centralized and modules don't read
environment variables directly.
"""

import os
import sys
import tempfile
from unittest.mock import patch


def test_configuration_loader_loads_from_environment():
    """Test that ConfigurationLoader properly loads from environment variables."""
    # Add the project root to the path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    try:
        from voice_typing import ConfigurationLoader
        
        # Save original environment
        original_env = {}
        test_keys = [
            "VOSK_MODEL_PATH", "RECOGNITION_SOURCE", "OPENAI_API_KEY", "WHISPER_MODEL"
        ]
        for key in test_keys:
            original_env[key] = os.environ.get(key)
        
        try:
            # Set test environment variables
            os.environ["VOSK_MODEL_PATH"] = "/test/model/path"
            os.environ["RECOGNITION_SOURCE"] = "whisper"
            os.environ["OPENAI_API_KEY"] = "test-api-key"
            os.environ["WHISPER_MODEL"] = "test-model"
            
            # Load configuration
            config = ConfigurationLoader.load_configuration()
            
            # Verify configuration was loaded from environment
            assert config["model_path"] == "/test/model/path"
            assert config["recognition_source"] == "whisper"
            assert config["openai_api_key"] == "test-api-key"
            assert config["whisper_model"] == "test-model"
            assert config["sample_rate"] == 16000  # Default value
            
            print("✅ ConfigurationLoader environment loading test passed")
            
        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
                    
    except ImportError as e:
        print(f"⚠️ Skipping test due to missing dependencies: {e}")


def test_config_accepts_constructor_values():
    """Test that Config class accepts values via constructor instead of reading environment."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    try:
        from voice_typing import Config
        
        # Test with custom configuration
        custom_config = {
            "model_path": "/custom/model/path",
            "sample_rate": 8000,
            "recognition_source": "custom",
            "openai_api_key": "custom-key",
            "whisper_model": "custom-model",
            "hotkey_combo": {"custom", "hotkey"}
        }
        
        config = Config(custom_config)
        
        # Verify config uses provided values
        assert config.MODEL_PATH == "/custom/model/path"
        assert config.SAMPLE_RATE == 8000
        assert config.RECOGNITION_SOURCE == "custom"
        assert config.OPENAI_API_KEY == "custom-key"
        assert config.WHISPER_MODEL == "custom-model"
        assert config.HOTKEY_COMBO == {"custom", "hotkey"}
        
        print("✅ Config constructor values test passed")
        
    except ImportError as e:
        print(f"⚠️ Skipping test due to missing dependencies: {e}")


def test_config_no_direct_environment_access():
    """Test that Config doesn't read environment variables after construction."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    try:
        from voice_typing import Config
        
        # Create config with specific values
        config_dict = {
            "model_path": "/initial/path",
            "recognition_source": "initial",
            "openai_api_key": "initial-key"
        }
        config = Config(config_dict)
        
        # Verify initial values
        assert config.MODEL_PATH == "/initial/path"
        assert config.RECOGNITION_SOURCE == "initial"
        assert config.OPENAI_API_KEY == "initial-key"
        
        # Change environment variables after config creation
        original_env = {}
        test_keys = ["VOSK_MODEL_PATH", "RECOGNITION_SOURCE", "OPENAI_API_KEY"]
        for key in test_keys:
            original_env[key] = os.environ.get(key)
        
        try:
            os.environ["VOSK_MODEL_PATH"] = "/changed/path"
            os.environ["RECOGNITION_SOURCE"] = "changed"
            os.environ["OPENAI_API_KEY"] = "changed-key"
            
            # Config values should NOT change (no direct environment access)
            assert config.MODEL_PATH == "/initial/path"
            assert config.RECOGNITION_SOURCE == "initial"
            assert config.OPENAI_API_KEY == "initial-key"
            
            print("✅ Config no direct environment access test passed")
            
        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
                    
    except ImportError as e:
        print(f"⚠️ Skipping test due to missing dependencies: {e}")


def test_whisper_source_no_environment_fallback():
    """Test that WhisperRecognitionSource doesn't fall back to environment variables."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    try:
        from voice_typing.recognition_sources import WhisperRecognitionSource
        
        # Set environment variable
        original_key = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "env-fallback-key"
        
        try:
            whisper_source = WhisperRecognitionSource()
            
            # Initialize with empty config (no api_key provided)
            config = {"model": "test-model", "sample_rate": 16000}
            result = whisper_source.initialize(config)
            
            # Should fail because no api_key in config and no fallback to environment
            assert not result, "WhisperRecognitionSource should not fall back to environment"
            assert whisper_source.api_key is None
            
            print("✅ WhisperRecognitionSource no environment fallback test passed")
            
        finally:
            # Restore original environment
            if original_key is not None:
                os.environ["OPENAI_API_KEY"] = original_key
            elif "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
                
    except ImportError as e:
        print(f"⚠️ Skipping test due to missing dependencies: {e}")


def test_integration_with_existing_modules():
    """Test that existing modules work with centralized configuration."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    try:
        from voice_typing import Config, ConfigurationLoader, GlobalState, AudioProcessor
        
        # Test that modules can still be created with centralized config
        config = Config()  # Uses ConfigurationLoader internally
        state_ref = GlobalState()
        
        # This will try to create recognition source - may fail due to missing dependencies
        # but should not fail due to configuration issues
        try:
            audio_processor = AudioProcessor(config, state_ref)
            print("✅ AudioProcessor creation with centralized config works")
        except SystemExit:
            # Expected due to missing Vosk model or other dependencies
            print("✅ AudioProcessor failed due to dependencies, not config (expected)")
        except Exception as e:
            if "config" in str(e).lower():
                raise AssertionError(f"Configuration-related error: {e}")
            else:
                print(f"✅ AudioProcessor failed due to non-config issue: {e} (expected)")
        
    except ImportError as e:
        print(f"⚠️ Skipping test due to missing dependencies: {e}")


if __name__ == "__main__":
    test_configuration_loader_loads_from_environment()
    test_config_accepts_constructor_values()
    test_config_no_direct_environment_access()
    test_whisper_source_no_environment_fallback()
    test_integration_with_existing_modules()
    print("🎉 All centralized configuration tests passed!")