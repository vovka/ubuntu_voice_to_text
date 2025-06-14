"""
Centralized Configuration Loader Service.

This module provides a centralized way to load configuration from environment
variables, configuration files, or other sources. It decouples business logic
from direct environment variable access.
"""

import os
from typing import Dict, Any, Optional


class ConfigurationLoader:
    """
    Centralized configuration loader that reads from environment variables,
    configuration files, or other sources and provides a single point of
    configuration access.
    """

    @staticmethod
    def load_configuration() -> Dict[str, Any]:
        """
        Load configuration from environment variables and other sources.
        
        Returns:
            Dict[str, Any]: Complete configuration dictionary
        """
        config = {
            # Voice recognition configuration
            "model_path": os.getenv(
                "VOSK_MODEL_PATH", 
                os.path.expanduser("/models/vosk-model-small-en-us-0.15")
            ),
            "sample_rate": 16000,
            "recognition_source": os.getenv("RECOGNITION_SOURCE", "vosk"),
            
            # OpenAI/Whisper configuration
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "whisper_model": os.getenv("WHISPER_MODEL", "gpt-4o-transcribe"),
            
            # Hotkey configuration
            "hotkey_combo": ConfigurationLoader._load_hotkey_combo(),
        }
        
        return config
    
    @staticmethod
    def _load_hotkey_combo():
        """
        Load hotkey combination configuration.
        
        Returns:
            Set of hotkey objects or empty set if not available
        """
        try:
            from pynput import keyboard
            return {keyboard.Key.cmd, keyboard.Key.shift}  # Win+Shift
        except ImportError:
            # Fallback for testing without dependencies
            return set()
    
    @staticmethod
    def load_from_file(config_file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load configuration from a file (future enhancement).
        
        Args:
            config_file_path: Path to configuration file
            
        Returns:
            Optional[Dict[str, Any]]: Configuration from file or None if not found
        """
        # Future implementation for loading from JSON/YAML/INI files
        return None
    
    @staticmethod
    def merge_configurations(*configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge multiple configuration dictionaries.
        Later configurations override earlier ones.
        
        Args:
            *configs: Configuration dictionaries to merge
            
        Returns:
            Dict[str, Any]: Merged configuration
        """
        merged = {}
        for config in configs:
            if config:
                merged.update(config)
        return merged