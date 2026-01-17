from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    # Application
    app_name: str = "Tamil Speech Learning Backend"
    debug: bool = False
    api_version: str = "v1"

    # Database
    database_url: str

    # JWT Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Provider Selection
    stt_provider: str = "azure"  # azure, google, whisper
    tts_provider: str = "azure"  # azure, google, elevenlabs
    llm_provider: str = "groq"   # groq, openai, anthropic

    # Azure Speech Services
    azure_speech_key: Optional[str] = None
    azure_speech_region: Optional[str] = None
    azure_speech_language: str = "ta-IN"  # Tamil India

    # Groq LLM
    groq_api_key: Optional[str] = None
    groq_model: str = "mixtral-8x7b-32768"

    # Google Cloud (optional)
    google_credentials_path: Optional[str] = None

    # OpenAI (optional)
    openai_api_key: Optional[str] = None

    # CORS
    cors_origins: list[str] = ["*"]

    # Speech Analysis
    phoneme_similarity_threshold: float = 0.8
    word_similarity_threshold: float = 0.7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
