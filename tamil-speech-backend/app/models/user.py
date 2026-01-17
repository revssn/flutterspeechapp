from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class User(SQLModel, table=True):
    """User model for authentication and profile management."""

    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    email: str = Field(unique=True, index=True, nullable=False, max_length=255)
    password_hash: str = Field(nullable=False)
    display_name: str = Field(nullable=False, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # User settings as JSON (preferences, UI settings, etc.)
    settings: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Account status
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)


class UserCreate(SQLModel):
    """Schema for user registration."""
    email: str
    password: str
    display_name: str


class UserLogin(SQLModel):
    """Schema for user login."""
    email: str
    password: str


class UserResponse(SQLModel):
    """Schema for user response (without password)."""
    id: uuid.UUID
    email: str
    display_name: str
    created_at: datetime
    settings: Dict[str, Any]
    is_active: bool
    is_verified: bool


class Token(SQLModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    """Schema for token payload data."""
    user_id: Optional[uuid.UUID] = None
    email: Optional[str] = None
