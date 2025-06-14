"""
OpenAI Whisper ASR implementation of voice recognition source.
"""

import os
import tempfile
import wave
from typing import Dict, Any, Optional
from .base import VoiceRecognitionSource

DEFAULT_WHISPER_MODEL = "gpt-4o-transcribe"


class WhisperRecognitionSource(VoiceRecognitionSource):
    """OpenAI Whisper ASR-based voice recognition source."""

    def __init__(self):
        self.client = None
        self.api_key = None
        self.model = DEFAULT_WHISPER_MODEL
        self.sample_rate = 16000
        self._is_available = False
        self._audio_buffer = bytearray()
        self._last_result = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize OpenAI Whisper recognition source.

        Args:
            config: Configuration dictionary with 'api_key', 'model', and 'sample_rate'

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        self.api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        self.model = config.get("model", "gpt-4o-transcribe")
        self.sample_rate = config.get("sample_rate", 16000)

        if not self.api_key:
            print("[WhisperRecognitionSource] ❌ OpenAI API key not provided")
            return False

        try:
            import openai

            self.client = openai.OpenAI(api_key=self.api_key)
            self._is_available = True
            print(
                f"[WhisperRecognitionSource] ✅ OpenAI Whisper initialized "
                f"with model: {self.model}"
            )
            return True
        except ImportError:
            print(
                "[WhisperRecognitionSource] openai package not available, "
                "recognition disabled"
            )
            return False
        except Exception as e:
            print(f"[WhisperRecognitionSource] Error initializing OpenAI Whisper: {e}")
            return False

    def process_audio_chunk(self, audio_chunk: bytes) -> None:
        """
        Process a chunk of audio data by accumulating it for later API call.

        Args:
            audio_chunk: Raw audio data in bytes
        """
        if self._is_available:
            self._audio_buffer.extend(audio_chunk)

    def get_result(self) -> Optional[Dict[str, Any]]:
        """
        Get the recognition result from OpenAI Whisper API.
        This processes all accumulated audio chunks and returns the result.

        Returns:
            Optional[Dict[str, Any]]: Recognition result dictionary or None if no result
        """
        if not self._is_available or not self._audio_buffer:
            return self._last_result

        try:
            # Create a temporary WAV file from the accumulated audio buffer
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                self._create_wav_file(temp_file.name, bytes(self._audio_buffer))

                # Send audio to OpenAI Whisper API
                with open(temp_file.name, "rb") as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model=self.model, file=audio_file, response_format="json"
                    )

                # Clean up temporary file
                os.unlink(temp_file.name)

                # Clear buffer after processing
                self._audio_buffer.clear()

                # Store and return result
                result = {"text": transcript.text.strip()}
                self._last_result = result if result["text"] else None
                return self._last_result

        except Exception as e:
            print(f"[WhisperRecognitionSource] Error getting result from API: {e}")
            # Clear buffer on error to avoid reprocessing same audio
            self._audio_buffer.clear()
            return None

    def _create_wav_file(self, filename: str, audio_data: bytes) -> None:
        """
        Create a WAV file from raw audio bytes.

        Args:
            filename: Output WAV file path
            audio_data: Raw audio data in bytes
        """
        with wave.open(filename, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data)

    def is_available(self) -> bool:
        """
        Check if OpenAI Whisper recognition source is available.

        Returns:
            bool: True if available, False otherwise
        """
        return self._is_available

    def cleanup(self) -> None:
        """
        Clean up Whisper resources.
        """
        self.client = None
        self._audio_buffer.clear()
        self._last_result = None
        self._is_available = False
