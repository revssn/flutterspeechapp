"""Progress tracking service for learning activities."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.progress import LearningProgress, ProgressCreate, ProgressUpdate
from typing import List, Optional
import uuid
from datetime import datetime


class ProgressService:
    """Service for tracking user learning progress."""

    async def get_user_progress(
        self,
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> List[LearningProgress]:
        """
        Get all progress records for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of progress records
        """
        result = await db.execute(
            select(LearningProgress)
            .where(LearningProgress.user_id == user_id)
            .order_by(LearningProgress.last_attempt_at.desc())
        )
        return list(result.scalars().all())

    async def get_situation_progress(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        situation_id: uuid.UUID
    ) -> List[LearningProgress]:
        """
        Get progress for a specific situation.

        Args:
            db: Database session
            user_id: User ID
            situation_id: Situation ID

        Returns:
            List of progress records for the situation
        """
        result = await db.execute(
            select(LearningProgress)
            .where(
                and_(
                    LearningProgress.user_id == user_id,
                    LearningProgress.situation_id == situation_id
                )
            )
            .order_by(LearningProgress.last_attempt_at.desc())
        )
        return list(result.scalars().all())

    async def get_or_create_progress(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        situation_id: uuid.UUID,
        content_type: str,
        content_id: Optional[str] = None
    ) -> LearningProgress:
        """
        Get existing progress or create new one.

        Args:
            db: Database session
            user_id: User ID
            situation_id: Situation ID
            content_type: Type of content (word, phrase, conversation)
            content_id: Optional content identifier

        Returns:
            LearningProgress record
        """
        # Try to find existing progress
        query = select(LearningProgress).where(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.situation_id == situation_id,
                LearningProgress.content_type == content_type
            )
        )

        if content_id:
            query = query.where(LearningProgress.content_id == content_id)

        result = await db.execute(query)
        progress = result.scalar_one_or_none()

        if progress:
            return progress

        # Create new progress record
        progress = LearningProgress(
            user_id=user_id,
            situation_id=situation_id,
            content_type=content_type,
            content_id=content_id
        )
        db.add(progress)
        await db.commit()
        await db.refresh(progress)

        return progress

    async def update_progress(
        self,
        db: AsyncSession,
        progress_id: uuid.UUID,
        score: float,
        completed: bool = False
    ) -> LearningProgress:
        """
        Update progress with new attempt.

        Args:
            db: Database session
            progress_id: Progress record ID
            score: Score for this attempt (0-100)
            completed: Whether the content is completed

        Returns:
            Updated LearningProgress record
        """
        result = await db.execute(
            select(LearningProgress).where(LearningProgress.id == progress_id)
        )
        progress = result.scalar_one()

        # Update attempts count
        progress.attempts += 1

        # Update best score
        if score > progress.best_score:
            progress.best_score = score

        # Calculate new average score
        # Using incremental average formula
        current_avg = progress.average_score
        new_avg = current_avg + (score - current_avg) / progress.attempts
        progress.average_score = round(new_avg, 2)

        # Update timestamps
        progress.last_attempt_at = datetime.utcnow()

        # Update completion status
        if completed and not progress.completed:
            progress.completed = True
            progress.completed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(progress)

        return progress

    async def record_attempt(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        situation_id: uuid.UUID,
        content_type: str,
        score: float,
        content_id: Optional[str] = None,
        completed: bool = False
    ) -> LearningProgress:
        """
        Record a learning attempt (convenience method).

        Args:
            db: Database session
            user_id: User ID
            situation_id: Situation ID
            content_type: Type of content
            score: Score achieved
            content_id: Optional content identifier
            completed: Whether completed

        Returns:
            Updated LearningProgress record
        """
        # Get or create progress record
        progress = await self.get_or_create_progress(
            db=db,
            user_id=user_id,
            situation_id=situation_id,
            content_type=content_type,
            content_id=content_id
        )

        # Update with new attempt
        return await self.update_progress(
            db=db,
            progress_id=progress.id,
            score=score,
            completed=completed
        )

    async def get_completion_stats(
        self,
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> dict:
        """
        Get completion statistics for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary with completion stats
        """
        result = await db.execute(
            select(LearningProgress).where(LearningProgress.user_id == user_id)
        )
        all_progress = list(result.scalars().all())

        total_items = len(all_progress)
        completed_items = sum(1 for p in all_progress if p.completed)
        total_attempts = sum(p.attempts for p in all_progress)
        average_score = (
            sum(p.average_score for p in all_progress) / total_items
            if total_items > 0 else 0.0
        )

        return {
            "total_items": total_items,
            "completed_items": completed_items,
            "in_progress_items": total_items - completed_items,
            "completion_rate": round(completed_items / total_items * 100, 2) if total_items > 0 else 0.0,
            "total_attempts": total_attempts,
            "average_score": round(average_score, 2)
        }

    async def get_recent_activity(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 10
    ) -> List[LearningProgress]:
        """
        Get recent learning activity.

        Args:
            db: Database session
            user_id: User ID
            limit: Number of records to return

        Returns:
            List of recent progress records
        """
        result = await db.execute(
            select(LearningProgress)
            .where(LearningProgress.user_id == user_id)
            .order_by(LearningProgress.last_attempt_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
