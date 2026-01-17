"""Error analysis service for pronunciation mistakes."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.error import ErrorLog, UserErrorProfile, ErrorLogCreate
from app.models.user import User
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from collections import defaultdict
import Levenshtein


class ErrorAnalyzer:
    """Analyze pronunciation errors and build user profiles."""

    TAMIL_PHONEMES = [
        # Vowels
        "அ", "ஆ", "இ", "ஈ", "உ", "ஊ", "எ", "ஏ", "ஐ", "ஒ", "ஓ", "ஔ",
        # Consonants
        "க", "ங", "ச", "ஞ", "ட", "ண", "த", "ந", "ப", "ம",
        "ய", "ர", "ல", "வ", "ழ", "ள", "ற", "ன",
        # Special characters
        "ஃ"
    ]

    async def analyze_pronunciation_error(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        expected_text: str,
        spoken_text: str,
        situation_id: Optional[uuid.UUID] = None,
        audio_duration: Optional[float] = None
    ) -> ErrorLog:
        """
        Analyze a pronunciation error and log it.

        Args:
            db: Database session
            user_id: User ID
            expected_text: Text that should have been spoken
            spoken_text: Text that was actually spoken
            situation_id: Optional situation context
            audio_duration: Duration of audio in seconds

        Returns:
            Created ErrorLog entry
        """
        # Analyze phoneme-level errors
        phoneme_errors = self._analyze_phoneme_errors(expected_text, spoken_text)

        # Identify mispronounced words
        word_errors = self._identify_word_errors(expected_text, spoken_text)

        # Calculate scores
        score = self._calculate_score(expected_text, spoken_text)
        similarity_score = self._calculate_similarity(expected_text, spoken_text)

        # Create error log
        error_log = ErrorLog(
            user_id=user_id,
            situation_id=situation_id,
            expected_text=expected_text,
            spoken_text=spoken_text,
            phoneme_errors=phoneme_errors,
            word_errors=word_errors,
            score=score,
            similarity_score=similarity_score,
            audio_duration=audio_duration
        )

        db.add(error_log)
        await db.commit()
        await db.refresh(error_log)

        # Update user error profile
        await self._update_user_error_profile(db, user_id)

        return error_log

    def _analyze_phoneme_errors(
        self,
        expected: str,
        spoken: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze errors at the phoneme level.

        Returns:
            List of phoneme error dictionaries
        """
        errors = []

        # Simple character-by-character comparison
        # In production, you'd use proper phoneme extraction
        max_len = max(len(expected), len(spoken))

        for i in range(max_len):
            expected_char = expected[i] if i < len(expected) else ""
            spoken_char = spoken[i] if i < len(spoken) else ""

            if expected_char != spoken_char:
                if expected_char and spoken_char:
                    # Substitution
                    if expected_char in self.TAMIL_PHONEMES:
                        errors.append({
                            "phoneme": expected_char,
                            "position": i,
                            "error_type": "substitution",
                            "actual": spoken_char
                        })
                elif expected_char:
                    # Deletion
                    if expected_char in self.TAMIL_PHONEMES:
                        errors.append({
                            "phoneme": expected_char,
                            "position": i,
                            "error_type": "deletion",
                            "actual": ""
                        })
                else:
                    # Insertion
                    errors.append({
                        "phoneme": spoken_char,
                        "position": i,
                        "error_type": "insertion",
                        "actual": spoken_char
                    })

        return errors

    def _identify_word_errors(self, expected: str, spoken: str) -> List[str]:
        """Identify which words were mispronounced."""
        expected_words = expected.split()
        spoken_words = spoken.split()

        error_words = []

        # Compare word by word
        for i in range(min(len(expected_words), len(spoken_words))):
            if expected_words[i] != spoken_words[i]:
                # Check if it's a significant difference
                similarity = Levenshtein.ratio(expected_words[i], spoken_words[i])
                if similarity < 0.8:  # 80% threshold
                    error_words.append(expected_words[i])

        # Add any missing words
        if len(expected_words) > len(spoken_words):
            error_words.extend(expected_words[len(spoken_words):])

        return error_words

    def _calculate_score(self, expected: str, spoken: str) -> float:
        """Calculate pronunciation score (0-100)."""
        if not expected:
            return 0.0

        similarity = Levenshtein.ratio(expected, spoken)
        return round(similarity * 100, 2)

    def _calculate_similarity(self, expected: str, spoken: str) -> float:
        """Calculate Levenshtein similarity ratio."""
        return round(Levenshtein.ratio(expected, spoken), 4)

    async def _update_user_error_profile(
        self,
        db: AsyncSession,
        user_id: uuid.UUID
    ):
        """
        Update user's error profile based on error history.

        Args:
            db: Database session
            user_id: User ID
        """
        # Get or create error profile
        result = await db.execute(
            select(UserErrorProfile).where(UserErrorProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            profile = UserErrorProfile(user_id=user_id)
            db.add(profile)

        # Get all user errors
        errors_result = await db.execute(
            select(ErrorLog).where(ErrorLog.user_id == user_id)
        )
        all_errors = errors_result.scalars().all()

        # Analyze weak phonemes
        phoneme_stats = defaultdict(lambda: {"count": 0, "total_attempts": 0})

        for error in all_errors:
            for phoneme_error in error.phoneme_errors:
                phoneme = phoneme_error.get("phoneme")
                if phoneme:
                    phoneme_stats[phoneme]["count"] += 1

            # Count total attempts for each phoneme (simplified)
            for char in error.expected_text:
                if char in self.TAMIL_PHONEMES:
                    phoneme_stats[char]["total_attempts"] += 1

        # Calculate accuracy for each phoneme
        weak_phonemes = []
        for phoneme, stats in phoneme_stats.items():
            if stats["total_attempts"] > 0:
                accuracy = 1 - (stats["count"] / stats["total_attempts"])
                if accuracy < 0.8:  # Less than 80% accuracy
                    weak_phonemes.append({
                        "phoneme": phoneme,
                        "error_count": stats["count"],
                        "accuracy": round(accuracy, 2)
                    })

        # Sort by error count (most errors first)
        weak_phonemes.sort(key=lambda x: x["error_count"], reverse=True)

        # Analyze weak words
        word_stats = defaultdict(int)
        for error in all_errors:
            for word in error.word_errors:
                word_stats[word] += 1

        weak_words = [
            {"word": word, "error_count": count, "accuracy": 0.5}  # Simplified
            for word, count in sorted(
                word_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]  # Top 20 problematic words
        ]

        # Calculate error frequency by type
        error_frequency = defaultdict(int)
        for error in all_errors:
            for phoneme_error in error.phoneme_errors:
                error_type = phoneme_error.get("error_type", "unknown")
                error_frequency[error_type] += 1

        # Calculate statistics
        total_attempts = len(all_errors)
        total_errors = sum(len(e.phoneme_errors) for e in all_errors)
        average_score = (
            sum(e.score for e in all_errors) / total_attempts
            if total_attempts > 0 else 0.0
        )

        # Update profile
        profile.weak_phonemes = weak_phonemes
        profile.weak_words = weak_words
        profile.total_attempts = total_attempts
        profile.total_errors = total_errors
        profile.average_score = round(average_score, 2)
        profile.error_frequency = dict(error_frequency)
        profile.updated_at = datetime.utcnow()
        profile.last_analyzed_at = datetime.utcnow()

        await db.commit()

    async def get_user_error_profile(
        self,
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> Optional[UserErrorProfile]:
        """Get user's error profile."""
        result = await db.execute(
            select(UserErrorProfile).where(UserErrorProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_error_history(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 50
    ) -> List[ErrorLog]:
        """Get user's error history."""
        result = await db.execute(
            select(ErrorLog)
            .where(ErrorLog.user_id == user_id)
            .order_by(ErrorLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
