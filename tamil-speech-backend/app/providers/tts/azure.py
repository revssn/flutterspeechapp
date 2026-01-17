"""Azure Text-to-Speech provider implementation."""

import azure.cognitiveservices.speech as speechsdk
from app.providers.base import TTSProvider, SynthesisResult
from app.config import settings
from typing import Optional, List, Dict, Any
import io


class AzureTTSProvider(TTSProvider):
    """Azure Speech Services TTS implementation."""

    # Tamil voice options in Azure
    TAMIL_VOICES = {
        "female": "ta-IN-PallaviNeural",
        "male": "ta-IN-ValluvarNeural",
    }

    def __init__(self):
        """Initialize Azure Speech Config."""
        if not settings.azure_speech_key or not settings.azure_speech_region:
            raise ValueError("Azure Speech credentials not configured")

        self.speech_config = speechsdk.SpeechConfig(
            subscription=settings.azure_speech_key,
            region=settings.azure_speech_region
        )

    async def synthesize(
        self,
        text: str,
        language: str = "ta-IN",
        voice: Optional[str] = None,
        audio_format: str = "wav"
    ) -> SynthesisResult:
        """
        Synthesize text to speech using Azure Speech Services.

        Args:
            text: Text to synthesize (Tamil text)
            language: Language code
            voice: Voice name (defaults to Tamil female neural voice)
            audio_format: Desired audio format

        Returns:
            SynthesisResult with audio data
        """
        # Set voice (default to Tamil female neural voice)
        if not voice:
            voice = self.TAMIL_VOICES["female"]
        self.speech_config.speech_synthesis_voice_name = voice

        # Set audio format
        if audio_format == "wav":
            self.speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
            )
        elif audio_format == "mp3":
            self.speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Audio24Khz96KBitRateMonoMp3
            )

        # Create synthesizer with null output (we'll get bytes)
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=None
        )

        # Synthesize
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Calculate duration (approximate from audio data)
            duration = len(result.audio_data) / 48000.0  # 24kHz 16-bit mono

            return SynthesisResult(
                audio_data=result.audio_data,
                audio_format=audio_format,
                duration=duration
            )
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            raise Exception(f"Speech synthesis canceled: {cancellation.reason}")
        else:
            raise Exception(f"Speech synthesis failed: {result.reason}")

    async def synthesize_with_visemes(
        self,
        text: str,
        language: str = "ta-IN",
        voice: Optional[str] = None,
        audio_format: str = "wav"
    ) -> SynthesisResult:
        """
        Synthesize text with viseme data for lip synchronization.

        Args:
            text: Text to synthesize
            language: Language code
            voice: Voice name
            audio_format: Desired audio format

        Returns:
            SynthesisResult with audio and viseme data
        """
        # Set voice
        if not voice:
            voice = self.TAMIL_VOICES["female"]
        self.speech_config.speech_synthesis_voice_name = voice

        # Set audio format
        if audio_format == "wav":
            self.speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
            )
        elif audio_format == "mp3":
            self.speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Audio24Khz96KBitRateMonoMp3
            )

        # Create synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=None
        )

        # Store visemes
        visemes: List[Dict[str, Any]] = []

        def viseme_callback(evt: speechsdk.SpeechSynthesisVisemeEventArgs):
            """Callback to capture viseme events."""
            visemes.append({
                "viseme_id": evt.viseme_id,
                "audio_offset": evt.audio_offset / 10000,  # Convert to milliseconds
                "animation": evt.animation
            })

        # Subscribe to viseme events
        synthesizer.viseme_received.connect(viseme_callback)

        # Synthesize
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Calculate duration
            duration = len(result.audio_data) / 48000.0  # 24kHz 16-bit mono

            return SynthesisResult(
                audio_data=result.audio_data,
                audio_format=audio_format,
                duration=duration,
                visemes=visemes if visemes else None
            )
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            raise Exception(f"Speech synthesis canceled: {cancellation.reason}")
        else:
            raise Exception(f"Speech synthesis failed: {result.reason}")

    def get_available_voices(self, language: str = "ta-IN") -> List[str]:
        """
        Get list of available Tamil voices.

        Returns:
            List of voice names
        """
        return list(self.TAMIL_VOICES.values())
