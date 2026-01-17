"""Speech routes for TTS, STT, and pronunciation evaluation."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.database import get_session
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.speech_service import get_speech_service
from app.services.error_analyzer import ErrorAnalyzer
from pydantic import BaseModel

router = APIRouter(prefix="/speech", tags=["Speech"])


class TTSRequest(BaseModel):
    """Request model for text-to-speech."""
    text: str
    language: str = "ta-IN"
    voice: Optional[str] = None
    audio_format: str = "wav"
    include_visemes: bool = False


class TTSResponse(BaseModel):
    """Response model for text-to-speech."""
    text: str
    audio_format: str
    duration: float
    visemes: Optional[list] = None


class TranscriptionResponse(BaseModel):
    """Response model for speech transcription."""
    text: str
    confidence: float
    language: str
    duration: Optional[float]


class EvaluationResponse(BaseModel):
    """Response model for pronunciation evaluation."""
    expected_text: str
    spoken_text: str
    confidence: float
    score: float
    similarity: float
    is_perfect: bool
    feedback: str


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(
    request: TTSRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Convert text to speech.

    Synthesizes Tamil text to audio with optional viseme data for lip sync.
    """
    speech_service = get_speech_service()

    try:
        if request.include_visemes:
            result = await speech_service.synthesize_with_visemes(
                text=request.text,
                language=request.language,
                voice=request.voice,
                audio_format=request.audio_format
            )
        else:
            result = await speech_service.synthesize_speech(
                text=request.text,
                language=request.language,
                voice=request.voice,
                audio_format=request.audio_format
            )

        return TTSResponse(
            text=request.text,
            audio_format=result.audio_format,
            duration=result.duration,
            visemes=result.visemes
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


@router.post("/tts/audio")
async def text_to_speech_audio(
    text: str = Form(...),
    language: str = Form("ta-IN"),
    voice: Optional[str] = Form(None),
    audio_format: str = Form("wav"),
    current_user: User = Depends(get_current_user)
):
    """
    Convert text to speech and return audio file directly.

    Returns the audio file as a binary response.
    """
    speech_service = get_speech_service()

    try:
        result = await speech_service.synthesize_speech(
            text=text,
            language=language,
            voice=voice,
            audio_format=audio_format
        )

        # Determine media type
        media_type = "audio/wav" if audio_format == "wav" else "audio/mpeg"

        return Response(
            content=result.audio_data,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=speech.{audio_format}"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form("ta-IN"),
    current_user: User = Depends(get_current_user)
):
    """
    Transcribe audio to text.

    Upload an audio file to get the Tamil text transcription.
    """
    speech_service = get_speech_service()

    try:
        # Read audio file
        audio_data = await audio.read()

        # Get audio format from filename
        audio_format = audio.filename.split(".")[-1] if audio.filename else "wav"

        # Transcribe
        result = await speech_service.transcribe_audio(
            audio_data=audio_data,
            language=language,
            audio_format=audio_format
        )

        return TranscriptionResponse(
            text=result.text,
            confidence=result.confidence,
            language=result.language,
            duration=result.duration
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_pronunciation(
    audio: UploadFile = File(...),
    expected_text: str = Form(...),
    language: str = Form("ta-IN"),
    situation_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Evaluate pronunciation by comparing audio to expected text.

    Upload audio and provide the expected text to get a pronunciation score.
    Optionally provide situation_id to log errors for analysis.
    """
    speech_service = get_speech_service()
    error_analyzer = ErrorAnalyzer()

    try:
        # Read audio file
        audio_data = await audio.read()

        # Get audio format
        audio_format = audio.filename.split(".")[-1] if audio.filename else "wav"

        # Evaluate pronunciation
        evaluation = await speech_service.evaluate_pronunciation(
            audio_data=audio_data,
            expected_text=expected_text,
            language=language
        )

        # Log error for analysis if situation_id is provided
        if situation_id:
            try:
                situation_uuid = uuid.UUID(situation_id)
                await error_analyzer.analyze_pronunciation_error(
                    db=db,
                    user_id=current_user.id,
                    expected_text=expected_text,
                    spoken_text=evaluation["spoken_text"],
                    situation_id=situation_uuid,
                    audio_duration=None
                )
            except ValueError:
                # Invalid UUID, skip error logging
                pass

        return EvaluationResponse(**evaluation)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pronunciation evaluation failed: {str(e)}"
        )
