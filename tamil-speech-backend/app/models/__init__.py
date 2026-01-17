"""Database models for the Tamil Speech Learning Backend."""

from app.models.user import (
    User,
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenData,
)
from app.models.progress import (
    LearningProgress,
    ProgressCreate,
    ProgressUpdate,
    ProgressResponse,
)
from app.models.error import (
    ErrorLog,
    UserErrorProfile,
    ErrorLogCreate,
    ErrorProfileResponse,
)
from app.models.situation import (
    Situation,
    ConversationSession,
    SituationCreate,
    SituationResponse,
    ConversationMessage,
    ConversationResponse,
)

__all__ = [
    # User models
    "User",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    # Progress models
    "LearningProgress",
    "ProgressCreate",
    "ProgressUpdate",
    "ProgressResponse",
    # Error models
    "ErrorLog",
    "UserErrorProfile",
    "ErrorLogCreate",
    "ErrorProfileResponse",
    # Situation models
    "Situation",
    "ConversationSession",
    "SituationCreate",
    "SituationResponse",
    "ConversationMessage",
    "ConversationResponse",
]
