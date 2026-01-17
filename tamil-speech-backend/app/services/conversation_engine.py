"""Conversation engine for real-time Tamil practice."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.situation import Situation, ConversationSession
from app.models.error import UserErrorProfile
from app.services.speech_service import get_speech_service
from app.services.error_analyzer import ErrorAnalyzer
from app.providers.llm.groq import GroqLLMProvider
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime


class ConversationEngine:
    """Engine for managing real-time Tamil conversation practice."""

    def __init__(self):
        """Initialize conversation engine."""
        self.speech_service = get_speech_service()
        self.error_analyzer = ErrorAnalyzer()
        self.llm_provider = GroqLLMProvider()

    async def start_conversation(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        situation_id: uuid.UUID
    ) -> ConversationSession:
        """
        Start a new conversation session.

        Args:
            db: Database session
            user_id: User ID
            situation_id: Situation ID

        Returns:
            Created ConversationSession
        """
        # Load situation
        situation = await self._get_situation(db, situation_id)
        if not situation:
            raise ValueError(f"Situation {situation_id} not found")

        # Create session
        session = ConversationSession(
            user_id=user_id,
            situation_id=situation_id,
            status="active",
            messages=[],
            errors_captured=[]
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        return session

    async def process_user_message(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        audio_data: bytes,
        expected_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user's audio message and generate response.

        Args:
            db: Database session
            session_id: Conversation session ID
            audio_data: User's audio input
            expected_text: Expected text (for pronunciation assessment)

        Returns:
            Dictionary with transcription, response, audio, and visemes
        """
        # Get session
        session = await self._get_session(db, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Load situation and user profile
        situation = await self._get_situation(db, session.situation_id)
        user_profile = await self.error_analyzer.get_user_error_profile(
            db, session.user_id
        )

        # Step 1: Transcribe user's speech
        transcription = await self.speech_service.transcribe_audio(
            audio_data=audio_data,
            language="ta-IN"
        )

        # Step 2: Analyze pronunciation if expected text is provided
        error_data = None
        if expected_text:
            error_log = await self.error_analyzer.analyze_pronunciation_error(
                db=db,
                user_id=session.user_id,
                expected_text=expected_text,
                spoken_text=transcription.text,
                situation_id=session.situation_id
            )
            error_data = {
                "score": error_log.score,
                "phoneme_errors": error_log.phoneme_errors,
                "word_errors": error_log.word_errors
            }

        # Step 3: Add user message to conversation
        user_message = {
            "role": "user",
            "content": transcription.text,
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": transcription.confidence
        }
        session.messages.append(user_message)

        # Step 4: Generate AI response using LLM
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in session.messages
        ]

        weak_phonemes = []
        if user_profile:
            weak_phonemes = [
                p["phoneme"] for p in user_profile.weak_phonemes[:5]
            ]

        vocabulary = [v["tamil"] for v in situation.vocabulary[:20]]

        response_text = await self.llm_provider.generate_conversation_response(
            conversation_history=conversation_history,
            situation_context=f"{situation.name_en}: {situation.description}",
            user_weak_phonemes=weak_phonemes,
            vocabulary=vocabulary
        )

        # Step 5: Synthesize response with visemes
        synthesis = await self.speech_service.synthesize_with_visemes(
            text=response_text,
            language="ta-IN"
        )

        # Step 6: Add AI message to conversation
        ai_message = {
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow().isoformat()
        }
        session.messages.append(ai_message)

        # Update session stats
        session.total_turns += 1
        if error_data:
            session.errors_captured.append(error_data)
            # Update average score
            scores = [e.get("score", 0) for e in session.errors_captured]
            session.average_score = sum(scores) / len(scores) if scores else 0.0

        # Calculate session duration
        session.duration_seconds = int(
            (datetime.utcnow() - session.started_at).total_seconds()
        )

        await db.commit()
        await db.refresh(session)

        return {
            "transcription": transcription.text,
            "transcription_confidence": transcription.confidence,
            "response_text": response_text,
            "response_audio": synthesis.audio_data,
            "audio_format": synthesis.audio_format,
            "visemes": synthesis.visemes,
            "pronunciation_assessment": error_data,
            "session_id": str(session.id),
            "turn_number": session.total_turns
        }

    async def get_conversation_starter(
        self,
        db: AsyncSession,
        situation_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Get a conversation starter for a situation.

        Args:
            db: Database session
            situation_id: Situation ID

        Returns:
            Dictionary with starter text, audio, and visemes
        """
        situation = await self._get_situation(db, situation_id)
        if not situation:
            raise ValueError(f"Situation {situation_id} not found")

        # Use first conversation starter or generate one
        if situation.conversation_starters:
            starter_text = situation.conversation_starters[0]
        else:
            starter_text = "வணக்கம்! எப்படி இருக்கிறீர்கள்?"  # Default greeting

        # Synthesize with visemes
        synthesis = await self.speech_service.synthesize_with_visemes(
            text=starter_text,
            language="ta-IN"
        )

        return {
            "text": starter_text,
            "audio": synthesis.audio_data,
            "audio_format": synthesis.audio_format,
            "visemes": synthesis.visemes,
            "situation": {
                "id": str(situation.id),
                "name_en": situation.name_en,
                "name_ta": situation.name_ta,
                "description": situation.description
            }
        }

    async def end_conversation(
        self,
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> ConversationSession:
        """
        End a conversation session.

        Args:
            db: Database session
            session_id: Session ID

        Returns:
            Updated ConversationSession
        """
        session = await self._get_session(db, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.status = "completed"
        session.ended_at = datetime.utcnow()
        session.duration_seconds = int(
            (session.ended_at - session.started_at).total_seconds()
        )

        await db.commit()
        await db.refresh(session)

        return session

    async def _get_situation(
        self,
        db: AsyncSession,
        situation_id: uuid.UUID
    ) -> Optional[Situation]:
        """Get situation by ID."""
        result = await db.execute(
            select(Situation).where(Situation.id == situation_id)
        )
        return result.scalar_one_or_none()

    async def _get_session(
        self,
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> Optional[ConversationSession]:
        """Get conversation session by ID."""
        result = await db.execute(
            select(ConversationSession).where(ConversationSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_session_summary(
        self,
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Get summary of a conversation session.

        Args:
            db: Database session
            session_id: Session ID

        Returns:
            Dictionary with session summary
        """
        session = await self._get_session(db, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        situation = await self._get_situation(db, session.situation_id)

        return {
            "session_id": str(session.id),
            "situation": {
                "id": str(situation.id),
                "name_en": situation.name_en,
                "name_ta": situation.name_ta
            } if situation else None,
            "status": session.status,
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "duration_seconds": session.duration_seconds,
            "total_turns": session.total_turns,
            "average_score": round(session.average_score, 2),
            "message_count": len(session.messages),
            "errors_count": len(session.errors_captured)
        }
