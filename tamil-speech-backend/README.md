# Tamil Speech Learning Backend

A comprehensive FastAPI backend for Tamil speech learning with AI-powered conversation practice, pronunciation assessment, and personalized error analysis.

## Features

- **Speech-to-Text (STT)**: Transcribe Tamil speech using Azure Speech Services
- **Text-to-Speech (TTS)**: Synthesize natural-sounding Tamil speech with viseme data for lip sync
- **Pronunciation Assessment**: Evaluate pronunciation accuracy with phoneme-level analysis
- **Error Profiling**: Track user's weak phonemes and words for personalized learning
- **AI Conversations**: Real-time conversation practice using Groq LLM with situation-based contexts
- **Progress Tracking**: Monitor learning progress across different situations
- **WebSocket Support**: Real-time bidirectional communication for conversation practice
- **Provider Abstraction**: Easily swap STT/TTS/LLM providers via configuration

## Architecture

```
tamil-speech-backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and ORM
│   ├── models/              # SQLModel database models
│   │   ├── user.py
│   │   ├── progress.py
│   │   ├── error.py
│   │   └── situation.py
│   ├── providers/           # Provider implementations
│   │   ├── base.py          # Abstract base classes
│   │   ├── stt/azure.py     # Azure STT
│   │   ├── tts/azure.py     # Azure TTS
│   │   └── llm/groq.py      # Groq LLM
│   ├── services/            # Business logic layer
│   │   ├── speech_service.py
│   │   ├── error_analyzer.py
│   │   ├── progress_service.py
│   │   └── conversation_engine.py
│   ├── routers/             # API endpoints
│   │   ├── auth.py
│   │   ├── speech.py
│   │   ├── progress.py
│   │   └── conversation.py
│   └── websocket/
│       └── conversation_ws.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### Prerequisites

- Python 3.10+
- Supabase account (for Postgres database)
- Azure Speech Services account
- Groq API key

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Configure environment variables in `.env`:
   - Set your Supabase database URL
   - Add Azure Speech Services credentials
   - Add Groq API key
   - Generate a secure JWT secret key

### Database Setup

The database tables will be created automatically on first run. The following tables are created:

- `users` - User accounts and authentication
- `learning_progress` - Progress tracking for learning activities
- `error_log` - Individual pronunciation error records
- `user_error_profile` - Aggregated error analysis per user
- `situations` - Real-world conversation scenarios
- `conversation_sessions` - Conversation practice sessions

### Running the Server

Development mode:
```bash
uvicorn app.main:app --reload
```

Production mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

Interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login (form data)
- `POST /auth/login/json` - Login (JSON)
- `GET /auth/me` - Get current user info
- `PUT /auth/me` - Update user profile

### Speech

- `POST /speech/tts` - Text to speech (returns JSON with audio)
- `POST /speech/tts/audio` - Text to speech (returns audio file)
- `POST /speech/transcribe` - Transcribe audio to text
- `POST /speech/evaluate` - Evaluate pronunciation

### Progress & Situations

- `GET /progress` - Get user's learning progress
- `GET /progress/stats` - Get completion statistics
- `GET /progress/situation/{id}` - Get progress for specific situation
- `GET /situations` - List all learning situations
- `GET /situations/{id}` - Get specific situation
- `POST /situations` - Create new situation

### Errors

- `GET /errors/profile` - Get user's error profile
- `GET /errors/history` - Get error history

### Conversation

- `POST /conversation/start/{situation_id}` - Start conversation session
- `POST /conversation/end/{session_id}` - End conversation session
- `GET /conversation/summary/{session_id}` - Get session summary
- `GET /conversation/starter/{situation_id}` - Get conversation starter
- `WS /ws/conversation/{session_id}` - WebSocket for real-time conversation

## WebSocket Protocol

### Connection

Connect to: `ws://localhost:8000/ws/conversation/{session_id}`

Query parameter: `token` (JWT authentication token)

### Client -> Server Messages

```json
{
  "type": "audio",
  "audio": "base64-encoded-audio-data",
  "expected_text": "optional expected text for assessment"
}
```

```json
{
  "type": "end"
}
```

### Server -> Client Messages

```json
{
  "type": "response",
  "transcription": "user's spoken text",
  "confidence": 0.95,
  "response_text": "AI response text",
  "response_audio": "base64-encoded-audio",
  "audio_format": "wav",
  "visemes": [...],
  "pronunciation_score": 85.5,
  "turn_number": 1
}
```

```json
{
  "type": "error",
  "message": "error description"
}
```

## Configuration

### Provider Configuration

You can swap providers by changing environment variables:

```env
STT_PROVIDER=azure  # azure, google, whisper
TTS_PROVIDER=azure  # azure, google, elevenlabs
LLM_PROVIDER=groq   # groq, openai, anthropic
```

### Speech Analysis Thresholds

Adjust pronunciation assessment thresholds:

```env
PHONEME_SIMILARITY_THRESHOLD=0.8
WORD_SIMILARITY_THRESHOLD=0.7
```

## Database Models

### User
- Authentication and profile information
- Settings and preferences

### LearningProgress
- Tracks attempts, scores, and completion status
- Per-situation and per-content tracking

### ErrorLog
- Individual pronunciation errors
- Phoneme-level and word-level analysis

### UserErrorProfile
- Aggregated weak phonemes and words
- Error frequency and improvement trends

### Situation
- Real-world conversation scenarios
- Vocabulary and conversation starters
- Difficulty levels and categories

### ConversationSession
- Real-time conversation tracking
- Message history and error capture

## Development

### Adding a New Provider

1. Create a new file in the appropriate provider directory
2. Implement the base class interface (STTProvider, TTSProvider, or LLMProvider)
3. Update the service to support the new provider
4. Add configuration options in `config.py`

Example:
```python
from app.providers.base import STTProvider, TranscriptionResult

class GoogleSTTProvider(STTProvider):
    async def transcribe(self, audio_data, language, audio_format):
        # Implementation
        pass
```

### Testing

Run tests with pytest:
```bash
pytest
```

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
