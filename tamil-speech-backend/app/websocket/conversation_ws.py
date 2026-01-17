"""WebSocket endpoint for real-time conversation practice."""

from fastapi import WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
import uuid
import base64

from app.database import get_session
from app.services.conversation_engine import ConversationEngine
from app.models.user import User


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """Accept and store a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        """Send a message to a specific connection."""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connections."""
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


async def websocket_conversation(
    websocket: WebSocket,
    session_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time conversation practice.

    Protocol:
    - Client connects with session_id and authentication token
    - Client sends audio messages as base64-encoded audio data
    - Server responds with transcription, AI response, and audio
    - Messages are JSON formatted

    Message format (client -> server):
    {
        "type": "audio",
        "audio": "base64-encoded-audio-data",
        "expected_text": "optional expected text for pronunciation assessment"
    }

    Message format (server -> client):
    {
        "type": "response",
        "transcription": "user's spoken text",
        "confidence": 0.95,
        "response_text": "AI response text",
        "response_audio": "base64-encoded-audio",
        "audio_format": "wav",
        "visemes": [...],
        "pronunciation_score": 85.5,  # if expected_text was provided
        "turn_number": 1
    }

    Error message format:
    {
        "type": "error",
        "message": "error description"
    }
    """
    # Validate session_id
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        await websocket.close(code=1008, reason="Invalid session ID")
        return

    # TODO: Validate authentication token
    # For now, we'll accept any connection
    # In production, you should validate the JWT token here

    # Accept connection
    await manager.connect(session_id, websocket)

    # Get database session
    async for db in get_session():
        engine = ConversationEngine()

        try:
            # Send welcome message
            await manager.send_message(session_id, {
                "type": "connected",
                "session_id": session_id,
                "message": "Connected to conversation session"
            })

            # Main message loop
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("type") == "audio":
                    try:
                        # Decode base64 audio
                        audio_base64 = message.get("audio")
                        if not audio_base64:
                            await manager.send_message(session_id, {
                                "type": "error",
                                "message": "No audio data provided"
                            })
                            continue

                        audio_data = base64.b64decode(audio_base64)

                        # Get optional expected text
                        expected_text = message.get("expected_text")

                        # Process user message
                        result = await engine.process_user_message(
                            db=db,
                            session_id=session_uuid,
                            audio_data=audio_data,
                            expected_text=expected_text
                        )

                        # Encode response audio as base64
                        response_audio_base64 = base64.b64encode(
                            result["response_audio"]
                        ).decode('utf-8')

                        # Build response
                        response = {
                            "type": "response",
                            "transcription": result["transcription"],
                            "confidence": result["transcription_confidence"],
                            "response_text": result["response_text"],
                            "response_audio": response_audio_base64,
                            "audio_format": result["audio_format"],
                            "visemes": result["visemes"],
                            "turn_number": result["turn_number"]
                        }

                        # Add pronunciation assessment if available
                        if result.get("pronunciation_assessment"):
                            assessment = result["pronunciation_assessment"]
                            response["pronunciation_score"] = assessment["score"]
                            response["phoneme_errors"] = assessment["phoneme_errors"]
                            response["word_errors"] = assessment["word_errors"]

                        # Send response to client
                        await manager.send_message(session_id, response)

                    except Exception as e:
                        await manager.send_message(session_id, {
                            "type": "error",
                            "message": f"Error processing audio: {str(e)}"
                        })

                elif message.get("type") == "end":
                    # End the conversation session
                    try:
                        summary = await engine.get_session_summary(
                            db=db,
                            session_id=session_uuid
                        )

                        await manager.send_message(session_id, {
                            "type": "ended",
                            "summary": summary
                        })

                        break

                    except Exception as e:
                        await manager.send_message(session_id, {
                            "type": "error",
                            "message": f"Error ending session: {str(e)}"
                        })

                else:
                    await manager.send_message(session_id, {
                        "type": "error",
                        "message": f"Unknown message type: {message.get('type')}"
                    })

        except WebSocketDisconnect:
            manager.disconnect(session_id)
            print(f"Client disconnected from session {session_id}")

        except Exception as e:
            print(f"WebSocket error: {str(e)}")
            manager.disconnect(session_id)
            try:
                await websocket.close(code=1011, reason=str(e))
            except:
                pass

        finally:
            manager.disconnect(session_id)
            await db.close()
