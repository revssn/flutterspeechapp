"""Speech service for STT and TTS operations."""

from app.providers.base import STTProvider, TTSProvider, TranscriptionResult, SynthesisResult
from app.providers.stt.azure import AzureSTTProvider
from app.providers.tts.azure import AzureTTSProvider
from app.config import settings
from typing import Optional
import Levenshtein


class SpeechService:
    """Service for handling speech recognition and synthesis."""

    def __init__(self):
        """Initialize speech providers based on configuration."""
        self.stt_provider: STTProvider = self._get_stt_provider()
        self.tts_provider: TTSProvider = self._get_tts_provider()

    def _get_stt_provider(self) -> STTProvider:
        """Get STT provider based on configuration."""
        if settings.stt_provider == "azure":
            return AzureSTTProvider()
        # Add other providers here (Google, Whisper, etc.)
        else:
            raise ValueError(f"Unknown STT provider: {settings.stt_provider}")

    def _get_tts_provider(self) -> TTSProvider:
        """Get TTS provider based on configuration."""
        if settings.tts_provider == "azure":
            return AzureTTSProvider()
        # Add other providers here (Google, ElevenLabs, etc.)
        else:
            raise ValueError(f"Unknown TTS provider: {settings.tts_provider}")

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "ta-IN",
        audio_format: str = "wav"
    ) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio_data: Audio bytes
            language: Language code
            audio_format: Audio format

        Returns:
            TranscriptionResult
        """
        return await self.stt_provider.transcribe(
            audio_data=audio_data,
            language=language,
            audio_format=audio_format
        )

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
            TranscriptionResult with phonemes
        """
        return await self.stt_provider.transcribe_with_phonemes(
            audio_data=audio_data,
            language=language,
            audio_format=audio_format
        )

    async def synthesize_speech(
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
            voice: Voice name (optional)
            audio_format: Desired audio format

        Returns:
            SynthesisResult
        """
        return await self.tts_provider.synthesize(
            text=text,
            language=language,
            voice=voice,
            audio_format=audio_format
        )

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
            voice: Voice name (optional)
            audio_format: Desired audio format

        Returns:
            SynthesisResult with visemes
        """
        return await self.tts_provider.synthesize_with_visemes(
            text=text,
            language=language,
            voice=voice,
            audio_format=audio_format
        )

    def calculate_pronunciation_score(
        self,
        expected_text: str,
        spoken_text: str
    ) -> dict:
        """
        Calculate pronunciation accuracy score.

        Args:
            expected_text: The text that should have been spoken
            spoken_text: The text that was actually spoken

        Returns:
            Dictionary with score and similarity metrics
        """
        # Normalize texts
        expected = expected_text.lower().strip()
        spoken = spoken_text.lower().strip()

        # Calculate Levenshtein distance and similarity
        distance = Levenshtein.distance(expected, spoken)
        max_len = max(len(expected), len(spoken))
        similarity = 1 - (distance / max_len) if max_len > 0 else 1.0

        # Convert to 0-100 score
        score = similarity * 100

        return {
            "score": round(score, 2),
            "similarity": round(similarity, 4),
            "distance": distance,
            "expected_length": len(expected),
            "spoken_length": len(spoken),
            "is_perfect": expected == spoken
        }

    async def evaluate_pronunciation(
        self,
        audio_data: bytes,
        expected_text: str,
        language: str = "ta-IN"
    ) -> dict:
        """
        Evaluate pronunciation by comparing audio to expected text.

        Args:
            audio_data: Audio bytes of the speech
            expected_text: The text that should have been spoken
            language: Language code

        Returns:
            Dictionary with transcription, score, and analysis
        """
        # Transcribe the audio
        transcription = await self.transcribe_audio(
            audio_data=audio_data,
            language=language
        )

        # Calculate pronunciation score
        score_data = self.calculate_pronunciation_score(
            expected_text=expected_text,
            spoken_text=transcription.text
        )

        return {
            "expected_text": expected_text,
            "spoken_text": transcription.text,
            "confidence": transcription.confidence,
            "score": score_data["score"],
            "similarity": score_data["similarity"],
            "is_perfect": score_data["is_perfect"],
            "feedback": self._generate_feedback(score_data["score"])
        }

    def _generate_feedback(self, score: float) -> str:
        """Generate encouraging feedback based on score."""
        if score >= 95:
            return "Perfect! Excellent pronunciation!"
        elif score >= 85:
            return "Great job! Very good pronunciation."
        elif score >= 70:
            return "Good effort! Keep practicing."
        elif score >= 50:
            return "Nice try! Let's practice some more."
        else:
            return "Keep going! Practice makes perfect."


# Singleton instance
_speech_service: Optional[SpeechService] = None


def get_speech_service() -> SpeechService:
    """Get or create the speech service singleton."""
    global _speech_service
    if _speech_service is None:
        _speech_service = SpeechService()
    return _speech_service
