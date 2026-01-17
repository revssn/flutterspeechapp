"""Conversation management routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import uuid

from app.database import get_session
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.conversation_engine import ConversationEngine

router = APIRouter(prefix="/conversation", tags=["Conversation"])


@router.post("/start/{situation_id}")
async def start_conversation(
    situation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    Start a new conversation session for a situation.

    Returns the session ID and initial conversation starter.
    """
    try:
        situation_uuid = uuid.UUID(situation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid situation ID")

    engine = ConversationEngine()

    try:
        # Start session
        session = await engine.start_conversation(
            db=db,
            user_id=current_user.id,
            situation_id=situation_uuid
        )

        # Get conversation starter
        starter = await engine.get_conversation_starter(
            db=db,
            situation_id=situation_uuid
        )

        return {
            "session_id": str(session.id),
            "situation": starter["situation"],
            "starter": {
                "text": starter["text"],
                "audio_format": starter["audio_format"],
                "visemes": starter["visemes"]
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start conversation: {str(e)}")


@router.post("/end/{session_id}")
async def end_conversation(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    End a conversation session.

    Returns session summary.
    """
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    engine = ConversationEngine()

    try:
        # End session
        session = await engine.end_conversation(
            db=db,
            session_id=session_uuid
        )

        # Get summary
        summary = await engine.get_session_summary(
            db=db,
            session_id=session_uuid
        )

        return summary

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end conversation: {str(e)}")


@router.get("/summary/{session_id}")
async def get_conversation_summary(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get summary of a conversation session.
    """
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    engine = ConversationEngine()

    try:
        summary = await engine.get_session_summary(
            db=db,
            session_id=session_uuid
        )

        return summary

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@router.get("/starter/{situation_id}")
async def get_conversation_starter(
    situation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get a conversation starter for a situation without starting a session.
    """
    try:
        situation_uuid = uuid.UUID(situation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid situation ID")

    engine = ConversationEngine()

    try:
        starter = await engine.get_conversation_starter(
            db=db,
            situation_id=situation_uuid
        )

        return starter

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get starter: {str(e)}")
