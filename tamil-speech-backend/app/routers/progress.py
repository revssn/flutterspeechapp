"""Progress tracking and error analysis routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.database import get_session
from app.models.user import User
from app.models.progress import ProgressResponse
from app.models.error import ErrorProfileResponse
from app.models.situation import Situation, SituationResponse, SituationCreate
from app.routers.auth import get_current_user
from app.services.progress_service import ProgressService
from app.services.error_analyzer import ErrorAnalyzer
from pydantic import BaseModel

router = APIRouter(tags=["Progress & Errors"])


class CompletionStatsResponse(BaseModel):
    """Response model for completion statistics."""
    total_items: int
    completed_items: int
    in_progress_items: int
    completion_rate: float
    total_attempts: int
    average_score: float


# Progress endpoints

@router.get("/progress", response_model=List[ProgressResponse])
async def get_my_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get all learning progress for current user."""
    progress_service = ProgressService()

    progress_list = await progress_service.get_user_progress(
        db=db,
        user_id=current_user.id
    )

    return progress_list


@router.get("/progress/stats", response_model=CompletionStatsResponse)
async def get_progress_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get completion statistics for current user."""
    progress_service = ProgressService()

    stats = await progress_service.get_completion_stats(
        db=db,
        user_id=current_user.id
    )

    return stats


@router.get("/progress/situation/{situation_id}", response_model=List[ProgressResponse])
async def get_situation_progress(
    situation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get progress for a specific situation."""
    try:
        situation_uuid = uuid.UUID(situation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid situation ID")

    progress_service = ProgressService()

    progress_list = await progress_service.get_situation_progress(
        db=db,
        user_id=current_user.id,
        situation_id=situation_uuid
    )

    return progress_list


# Error analysis endpoints

@router.get("/errors/profile", response_model=ErrorProfileResponse)
async def get_error_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get user's error profile with weak phonemes and words."""
    error_analyzer = ErrorAnalyzer()

    profile = await error_analyzer.get_user_error_profile(
        db=db,
        user_id=current_user.id
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Error profile not found")

    return profile


@router.get("/errors/history")
async def get_error_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get user's error history."""
    error_analyzer = ErrorAnalyzer()

    errors = await error_analyzer.get_user_error_history(
        db=db,
        user_id=current_user.id,
        limit=limit
    )

    return [
        {
            "id": str(error.id),
            "expected_text": error.expected_text,
            "spoken_text": error.spoken_text,
            "score": error.score,
            "similarity_score": error.similarity_score,
            "phoneme_errors": error.phoneme_errors,
            "word_errors": error.word_errors,
            "created_at": error.created_at.isoformat()
        }
        for error in errors
    ]


# Situation endpoints

@router.get("/situations", response_model=List[SituationResponse])
async def get_situations(
    difficulty: str = None,
    category: str = None,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all available learning situations."""
    query = select(Situation).where(Situation.is_active == True)

    if difficulty:
        query = query.where(Situation.difficulty == difficulty)

    if category:
        query = query.where(Situation.category == category)

    result = await db.execute(query.order_by(Situation.created_at))
    situations = result.scalars().all()

    return situations


@router.get("/situations/{situation_id}", response_model=SituationResponse)
async def get_situation(
    situation_id: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific situation by ID."""
    try:
        situation_uuid = uuid.UUID(situation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid situation ID")

    result = await db.execute(
        select(Situation).where(Situation.id == situation_uuid)
    )
    situation = result.scalar_one_or_none()

    if not situation:
        raise HTTPException(status_code=404, detail="Situation not found")

    return situation


@router.post("/situations", response_model=SituationResponse)
async def create_situation(
    situation_data: SituationCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new learning situation (admin only for now)."""
    situation = Situation(**situation_data.model_dump())

    db.add(situation)
    await db.commit()
    await db.refresh(situation)

    return situation
