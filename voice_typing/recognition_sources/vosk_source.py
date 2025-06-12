"""
Vosk implementation of voice recognition source.
"""

import json
import os
from typing import Dict, Any, Optional
from .base import VoiceRecognitionSource


class VoskRecognitionSource(VoiceRecognitionSource):
    """Vosk-based voice recognition source."""

    def __init__(self):
        self.model = None
        self.recognizer = None
        self._is_available = False

    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize Vosk recognition source.

        Args:
            config: Configuration dictionary with 'model_path' and 'sample_rate'

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        model_path = config.get("model_path")
        sample_rate = config.get("sample_rate", 16000)

        if not model_path or not os.path.exists(model_path):
            print(f"[VoskRecognitionSource] ❌ Vosk model not found at: {model_path}")
            return False

        try:
            import vosk

            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, sample_rate)
            self._is_available = True
            print(f"[VoskRecognitionSource] ✅ Vosk model loaded from: {model_path}")
            return True
        except ImportError:
            print("[VoskRecognitionSource] vosk not available, recognition disabled")
            return False
        except Exception as e:
            print(f"[VoskRecognitionSource] Error initializing Vosk: {e}")
            return False

    def process_audio_chunk(self, audio_chunk: bytes) -> None:
        """
        Process a chunk of audio data with Vosk.

        Args:
            audio_chunk: Raw audio data in bytes
        """
        if self.recognizer:
            self.recognizer.AcceptWaveform(audio_chunk)

    def get_result(self) -> Optional[Dict[str, Any]]:
        """
        Get the recognition result from Vosk.

        Returns:
            Optional[Dict[str, Any]]: Recognition result dictionary or None if no result
        """
        if not self.recognizer:
            return None

        try:
            result_json = self.recognizer.Result()
            result = json.loads(result_json)
            return result
        except (json.JSONDecodeError, Exception) as e:
            print(f"[VoskRecognitionSource] Error getting result: {e}")
            return None

    def is_available(self) -> bool:
        """
        Check if Vosk recognition source is available.

        Returns:
            bool: True if available, False otherwise
        """
        return self._is_available

    def cleanup(self) -> None:
        """
        Clean up Vosk resources.
        """
        # Vosk doesn't require explicit cleanup, but we can clear references
        self.model = None
        self.recognizer = None
        self._is_available = False
