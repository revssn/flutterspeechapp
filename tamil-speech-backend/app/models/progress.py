from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class LearningProgress(SQLModel, table=True):
    """Track user's learning progress for different content items."""

    __tablename__ = "learning_progress"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)
    situation_id: uuid.UUID = Field(foreign_key="situations.id", index=True, nullable=False)

    # Content tracking
    content_type: str = Field(nullable=False)  # "word", "phrase", "conversation"
    content_id: Optional[str] = None  # Reference to specific content item

    # Progress metrics
    attempts: int = Field(default=0)
    best_score: float = Field(default=0.0)  # 0-100
    average_score: float = Field(default=0.0)
    completed: bool = Field(default=False)

    # Timestamps
    first_attempt_at: datetime = Field(default_factory=datetime.utcnow)
    last_attempt_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class ProgressCreate(SQLModel):
    """Schema for creating progress record."""
    situation_id: uuid.UUID
    content_type: str
    content_id: Optional[str] = None


class ProgressUpdate(SQLModel):
    """Schema for updating progress."""
    score: float
    completed: bool = False


class ProgressResponse(SQLModel):
    """Schema for progress response."""
    id: uuid.UUID
    user_id: uuid.UUID
    situation_id: uuid.UUID
    content_type: str
    content_id: Optional[str]
    attempts: int
    best_score: float
    average_score: float
    completed: bool
    first_attempt_at: datetime
    last_attempt_at: datetime
    completed_at: Optional[datetime]
