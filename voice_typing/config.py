from typing import Dict, Any, Optional, Set
from .configuration_loader import ConfigurationLoader


class Config:
    """
    Configuration class that receives configuration values via constructor
    instead of reading environment variables directly.
    """
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration with provided values or load from ConfigurationLoader.
        
        Args:
            config_dict: Optional configuration dictionary. If None, loads using ConfigurationLoader.
        """
        if config_dict is None:
            config_dict = ConfigurationLoader.load_configuration()
        
        self._model_path = config_dict.get("model_path")
        self._sample_rate = config_dict.get("sample_rate", 16000)
        self._recognition_source = config_dict.get("recognition_source", "vosk")
        self._openai_api_key = config_dict.get("openai_api_key")
        self._whisper_model = config_dict.get("whisper_model", "gpt-4o-transcribe")
        self._hotkey_combo = config_dict.get("hotkey_combo", set())

    @property
    def MODEL_PATH(self) -> str:
        """Get model path."""
        return self._model_path

    @property
    def SAMPLE_RATE(self) -> int:
        """Get sample rate."""
        return self._sample_rate

    @property
    def RECOGNITION_SOURCE(self) -> str:
        """Get recognition source."""
        return self._recognition_source

    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        """Get OpenAI API key."""
        return self._openai_api_key

    @property
    def WHISPER_MODEL(self) -> str:
        """Get Whisper model."""
        return self._whisper_model

    @property
    def HOTKEY_COMBO(self) -> Set:
        """Get hotkey combination."""
        return self._hotkey_combo
