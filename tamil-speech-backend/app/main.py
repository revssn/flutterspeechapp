"""Main FastAPI application for Tamil Speech Learning Backend."""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import auth, speech, progress, conversation
from app.websocket.conversation_ws import websocket_conversation


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("🚀 Starting Tamil Speech Learning Backend...")
    print(f"📊 Database: {settings.database_url[:20]}...")
    print(f"🎤 STT Provider: {settings.stt_provider}")
    print(f"🔊 TTS Provider: {settings.tts_provider}")
    print(f"🤖 LLM Provider: {settings.llm_provider}")

    # Initialize database
    try:
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

    yield

    # Shutdown
    print("👋 Shutting down Tamil Speech Learning Backend...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description="Backend API for Tamil speech learning with AI-powered conversation practice",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.api_version,
        "providers": {
            "stt": settings.stt_provider,
            "tts": settings.tts_provider,
            "llm": settings.llm_provider
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }


# Include routers
app.include_router(auth.router)
app.include_router(speech.router)
app.include_router(progress.router)
app.include_router(conversation.router)


# WebSocket endpoint
@app.websocket("/ws/conversation/{session_id}")
async def conversation_websocket_endpoint(
    websocket: WebSocket,
    session_id: str
):
    """
    WebSocket endpoint for real-time conversation practice.

    Connect to this endpoint after creating a conversation session via POST /conversation/start/{situation_id}
    """
    await websocket_conversation(websocket, session_id)


# Additional utility endpoints
@app.get("/api/info")
async def api_info():
    """Get API information and available endpoints."""
    return {
        "app": settings.app_name,
        "version": settings.api_version,
        "endpoints": {
            "authentication": [
                "POST /auth/register - Register new user",
                "POST /auth/login - Login with form data",
                "POST /auth/login/json - Login with JSON",
                "GET /auth/me - Get current user info"
            ],
            "speech": [
                "POST /speech/tts - Text to speech",
                "POST /speech/tts/audio - Text to speech (audio file)",
                "POST /speech/transcribe - Transcribe audio",
                "POST /speech/evaluate - Evaluate pronunciation"
            ],
            "progress": [
                "GET /progress - Get user progress",
                "GET /progress/stats - Get completion stats",
                "GET /progress/situation/{id} - Get situation progress"
            ],
            "errors": [
                "GET /errors/profile - Get error profile",
                "GET /errors/history - Get error history"
            ],
            "situations": [
                "GET /situations - List all situations",
                "GET /situations/{id} - Get specific situation",
                "POST /situations - Create new situation"
            ],
            "conversation": [
                "POST /conversation/start/{situation_id} - Start conversation",
                "POST /conversation/end/{session_id} - End conversation",
                "GET /conversation/summary/{session_id} - Get session summary",
                "GET /conversation/starter/{situation_id} - Get conversation starter"
            ],
            "websocket": [
                "WS /ws/conversation/{session_id} - Real-time conversation"
            ]
        },
        "providers": {
            "stt": settings.stt_provider,
            "tts": settings.tts_provider,
            "llm": settings.llm_provider
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
