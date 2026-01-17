from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class Situation(SQLModel, table=True):
    """Real-world conversation situations for learning contexts."""

    __tablename__ = "situations"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

    # Situation details
    name_en: str = Field(nullable=False, max_length=100)  # English name
    name_ta: str = Field(nullable=False, max_length=100)  # Tamil name
    description: str = Field(nullable=False)  # Description of the situation

    # Difficulty and categorization
    difficulty: str = Field(default="beginner")  # beginner, intermediate, advanced
    category: str = Field(default="general")  # restaurant, travel, shopping, etc.

    # Learning content
    vocabulary: List[Dict[str, str]] = Field(default=[], sa_column=Column(JSON))
    # Format: [{"tamil": "வணக்கம்", "english": "hello", "phonetic": "vanakkam"}]

    conversation_starters: List[str] = Field(default=[], sa_column=Column(JSON))
    # Common opening phrases for this situation in Tamil

    sample_dialogues: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    # Format: [{"speaker": "customer", "text_ta": "...", "text_en": "..."}]

    # Metadata
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationSession(SQLModel, table=True):
    """Track real-time conversation sessions via WebSocket."""

    __tablename__ = "conversation_sessions"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)
    situation_id: uuid.UUID = Field(
        foreign_key="situations.id",
        index=True,
        nullable=False
    )

    # Session status
    status: str = Field(default="active")  # active, completed, abandoned
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None

    # Conversation data
    messages: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    # Format: [{"role": "user|assistant", "text": "...", "audio_url": "...", "timestamp": "..."}]

    errors_captured: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    # Errors made during this conversation

    # Metrics
    total_turns: int = Field(default=0)
    average_score: float = Field(default=0.0)
    duration_seconds: int = Field(default=0)


class SituationCreate(SQLModel):
    """Schema for creating a situation."""
    name_en: str
    name_ta: str
    description: str
    difficulty: str = "beginner"
    category: str = "general"
    vocabulary: List[Dict[str, str]] = []
    conversation_starters: List[str] = []
    sample_dialogues: List[Dict[str, Any]] = []


class SituationResponse(SQLModel):
    """Schema for situation response."""
    id: uuid.UUID
    name_en: str
    name_ta: str
    description: str
    difficulty: str
    category: str
    vocabulary: List[Dict[str, str]]
    conversation_starters: List[str]
    sample_dialogues: List[Dict[str, Any]]
    is_active: bool
    created_at: datetime


class ConversationMessage(SQLModel):
    """Schema for a single conversation message."""
    role: str  # "user" or "assistant"
    text: str
    audio_data: Optional[bytes] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationResponse(SQLModel):
    """Schema for conversation session response."""
    session_id: uuid.UUID
    situation_id: uuid.UUID
    status: str
    messages: List[Dict[str, Any]]
    errors_captured: List[Dict[str, Any]]
    total_turns: int
    average_score: float
