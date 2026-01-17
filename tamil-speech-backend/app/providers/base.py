"""Base classes for speech and LLM providers."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class TranscriptionResult:
    """Result from speech-to-text transcription."""
    text: str
    confidence: float
    language: str
    duration: Optional[float] = None
    phonemes: Optional[List[str]] = None


@dataclass
class SynthesisResult:
    """Result from text-to-speech synthesis."""
    audio_data: bytes
    audio_format: str  # "wav", "mp3", etc.
    duration: float
    visemes: Optional[List[Dict[str, Any]]] = None  # For lip sync


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    text: str
    model: str
    tokens_used: int
    finish_reason: str


class STTProvider(ABC):
    """Abstract base class for Speech-to-Text providers."""

    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "ta-IN",
        audio_format: str = "wav"
    ) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio_data: Audio bytes
            language: Language code (e.g., "ta-IN" for Tamil India)
            audio_format: Audio format (wav, mp3, etc.)

        Returns:
            TranscriptionResult with text and metadata
        """
        pass

    @abstractmethod
    async def transcribe_with_phonemes(
        self,
        audio_data: bytes,
        language: str = "ta-IN",
        audio_format: str = "wav"
    ) -> TranscriptionResult:
        """
        Transcribe audio with phoneme-level details.

        Args:
            audio_data: Audio bytes
            language: Language code
            audio_format: Audio format

        Returns:
            TranscriptionResult with phoneme information
        """
        pass


class TTSProvider(ABC):
    """Abstract base class for Text-to-Speech providers."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        language: str = "ta-IN",
        voice: Optional[str] = None,
        audio_format: str = "wav"
    ) -> SynthesisResult:
        """
        Synthesize text to speech.

        Args:
            text: Text to synthesize
            language: Language code
            voice: Voice name/ID (provider-specific)
            audio_format: Desired audio format

        Returns:
            SynthesisResult with audio data
        """
        pass

    @abstractmethod
    async def synthesize_with_visemes(
        self,
        text: str,
        language: str = "ta-IN",
        voice: Optional[str] = None,
        audio_format: str = "wav"
    ) -> SynthesisResult:
        """
        Synthesize text with viseme data for lip sync.

        Args:
            text: Text to synthesize
            language: Language code
            voice: Voice name/ID
            audio_format: Desired audio format

        Returns:
            SynthesisResult with audio and viseme data
        """
        pass


class LLMProvider(ABC):
    """Abstract base class for Large Language Model providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text completion.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Provider-specific parameters

        Returns:
            LLMResponse with generated text
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Chat completion with conversation history.

        Args:
            messages: List of {"role": "user|assistant", "content": "..."}
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Provider-specific parameters

        Returns:
            LLMResponse with generated text
        """
        pass
