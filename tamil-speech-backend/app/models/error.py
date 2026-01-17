from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid


class ErrorLog(SQLModel, table=True):
    """Log individual pronunciation errors for analysis."""

    __tablename__ = "error_log"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)
    situation_id: Optional[uuid.UUID] = Field(
        foreign_key="situations.id",
        index=True,
        nullable=True
    )

    # Speech data
    expected_text: str = Field(nullable=False)  # What should have been said
    spoken_text: str = Field(nullable=False)    # What was actually said

    # Error analysis
    phoneme_errors: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    # Format: [{"phoneme": "ழ", "position": 2, "error_type": "substitution", "actual": "ல"}]

    word_errors: List[str] = Field(default=[], sa_column=Column(JSON))
    # Words that were mispronounced

    # Scoring
    score: float = Field(default=0.0)  # 0-100 pronunciation accuracy
    similarity_score: float = Field(default=0.0)  # Levenshtein similarity

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    audio_duration: Optional[float] = None  # Duration in seconds


class UserErrorProfile(SQLModel, table=True):
    """Aggregated error profile for personalized learning."""

    __tablename__ = "user_error_profile"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        unique=True,
        index=True,
        nullable=False
    )

    # Weak areas (JSON arrays)
    weak_phonemes: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    # Format: [{"phoneme": "ழ", "error_count": 15, "accuracy": 0.65}]

    weak_words: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    # Format: [{"word": "வணக்கம்", "error_count": 8, "accuracy": 0.70}]

    # Statistics
    total_attempts: int = Field(default=0)
    total_errors: int = Field(default=0)
    average_score: float = Field(default=0.0)
    improvement_rate: float = Field(default=0.0)  # Trend over time

    # Error frequency by type
    error_frequency: Dict[str, int] = Field(default={}, sa_column=Column(JSON))
    # Format: {"substitution": 45, "deletion": 12, "insertion": 8}

    # Timestamps
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_analyzed_at: Optional[datetime] = None


class ErrorLogCreate(SQLModel):
    """Schema for creating error log."""
    situation_id: Optional[uuid.UUID] = None
    expected_text: str
    spoken_text: str
    phoneme_errors: List[Dict[str, Any]] = []
    word_errors: List[str] = []
    score: float
    similarity_score: float
    audio_duration: Optional[float] = None


class ErrorProfileResponse(SQLModel):
    """Schema for error profile response."""
    id: uuid.UUID
    user_id: uuid.UUID
    weak_phonemes: List[Dict[str, Any]]
    weak_words: List[Dict[str, Any]]
    total_attempts: int
    total_errors: int
    average_score: float
    improvement_rate: float
    error_frequency: Dict[str, int]
    updated_at: datetime
