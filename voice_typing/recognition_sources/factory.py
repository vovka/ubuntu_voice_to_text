"""
Recognition Source Factory for backend selection and instantiation.
"""

from typing import Dict, Any
from ..config import Config
from .base import VoiceRecognitionSource
from .vosk_source import VoskRecognitionSource
from .whisper_source import WhisperRecognitionSource


class RecognitionSourceFactory:
    """Factory for creating recognition source instances based on configuration."""
    
    @staticmethod
    def create_recognition_source(config: Config) -> VoiceRecognitionSource:
        """
        Create recognition source based on configuration.
        
        Args:
            config: Configuration object containing RECOGNITION_SOURCE setting
            
        Returns:
            VoiceRecognitionSource: Instance of the appropriate recognition source
        """
        source_type = config.RECOGNITION_SOURCE.lower()
        
        if source_type == "whisper":
            return WhisperRecognitionSource()
        elif source_type == "vosk":
            return VoskRecognitionSource()
        else:
            print(
                f"[RecognitionSourceFactory] ⚠️ Unknown recognition source '{source_type}', "
                "defaulting to Vosk"
            )
            return VoskRecognitionSource()
    
    @staticmethod
    def get_recognition_config(config: Config) -> Dict[str, Any]:
        """
        Get configuration dictionary for the recognition source.
        
        Args:
            config: Configuration object
            
        Returns:
            Dict[str, Any]: Configuration parameters for the recognition source
        """
        base_config = {
            "sample_rate": config.SAMPLE_RATE,
        }

        if config.RECOGNITION_SOURCE.lower() == "whisper":
            base_config.update(
                {
                    "api_key": config.OPENAI_API_KEY,
                    "model": config.WHISPER_MODEL,
                }
            )
        else:
            # Vosk configuration
            base_config.update(
                {
                    "model_path": config.MODEL_PATH,
                }
            )

        return base_config
    
    @staticmethod
    def get_available_sources() -> list:
        """
        Get list of available recognition source types.
        
        Returns:
            list: List of available source type strings
        """
        return ["vosk", "whisper"]