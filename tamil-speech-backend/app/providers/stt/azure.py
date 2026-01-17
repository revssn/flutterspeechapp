"""Azure Speech-to-Text provider implementation."""

import azure.cognitiveservices.speech as speechsdk
from app.providers.base import STTProvider, TranscriptionResult
from app.config import settings
from typing import Optional
import io


class AzureSTTProvider(STTProvider):
    """Azure Speech Services STT implementation."""

    def __init__(self):
        """Initialize Azure Speech Config."""
        if not settings.azure_speech_key or not settings.azure_speech_region:
            raise ValueError("Azure Speech credentials not configured")

        self.speech_config = speechsdk.SpeechConfig(
            subscription=settings.azure_speech_key,
            region=settings.azure_speech_region
        )

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "ta-IN",
        audio_format: str = "wav"
    ) -> TranscriptionResult:
        """
        Transcribe audio to text using Azure Speech Services.

        Args:
            audio_data: Audio bytes in WAV format
            language: Language code (default: Tamil India)
            audio_format: Audio format (currently only WAV supported)

        Returns:
            TranscriptionResult with transcribed text
        """
        # Configure speech recognition
        self.speech_config.speech_recognition_language = language

        # Create audio config from bytes
        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

        # Create speech recognizer
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )

        # Push audio data
        audio_stream.write(audio_data)
        audio_stream.close()

        # Perform recognition
        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # Calculate confidence (Azure provides this in JSON)
            confidence = 1.0  # Default if not available
            if hasattr(result, 'properties'):
                json_result = result.properties.get(
                    speechsdk.PropertyId.SpeechServiceResponse_JsonResult
                )
                if json_result:
                    import json
                    data = json.loads(json_result)
                    confidence = data.get('NBest', [{}])[0].get('Confidence', 1.0)

            return TranscriptionResult(
                text=result.text,
                confidence=confidence,
                language=language,
                duration=result.duration.total_seconds() if result.duration else None
            )
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return TranscriptionResult(
                text="",
                confidence=0.0,
                language=language,
                duration=0.0
            )
        else:
            raise Exception(f"Speech recognition failed: {result.reason}")

    async def transcribe_with_phonemes(
        self,
        audio_data: bytes,
        language: str = "ta-IN",
        audio_format: str = "wav"
    ) -> TranscriptionResult:
        """
        Transcribe with phoneme-level details for pronunciation assessment.

        Args:
            audio_data: Audio bytes
            language: Language code
            audio_format: Audio format

        Returns:
            TranscriptionResult with phoneme information
        """
        # Configure for pronunciation assessment
        self.speech_config.speech_recognition_language = language

        # Enable pronunciation assessment
        pronunciation_config = speechsdk.PronunciationAssessmentConfig(
            reference_text="",  # We'll do open-ended assessment
            grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
            granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
            enable_miscue=True
        )

        # Create audio config from bytes
        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

        # Create speech recognizer
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )

        # Apply pronunciation assessment
        pronunciation_config.apply_to(recognizer)

        # Push audio data
        audio_stream.write(audio_data)
        audio_stream.close()

        # Perform recognition
        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            phonemes = []
            confidence = 1.0

            # Extract phoneme data from pronunciation assessment
            if hasattr(result, 'properties'):
                json_result = result.properties.get(
                    speechsdk.PropertyId.SpeechServiceResponse_JsonResult
                )
                if json_result:
                    import json
                    data = json.loads(json_result)

                    # Extract phonemes from NBest results
                    nbest = data.get('NBest', [])
                    if nbest:
                        confidence = nbest[0].get('Confidence', 1.0)
                        words = nbest[0].get('Words', [])
                        for word in words:
                            word_phonemes = word.get('Phonemes', [])
                            phonemes.extend([p.get('Phoneme') for p in word_phonemes])

            return TranscriptionResult(
                text=result.text,
                confidence=confidence,
                language=language,
                duration=result.duration.total_seconds() if result.duration else None,
                phonemes=phonemes if phonemes else None
            )
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return TranscriptionResult(
                text="",
                confidence=0.0,
                language=language,
                duration=0.0,
                phonemes=[]
            )
        else:
            raise Exception(f"Speech recognition with phonemes failed: {result.reason}")
