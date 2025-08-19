"""
AI-Powered Voice-Controlled Task & Project Manager - FastAPI Backend

IMPORTANT FOR CLAUDE CODE:
- This is the main entry point for the voice AI backend
- All voice processing should be async and non-blocking
- Implement proper error handling for voice recognition failures
- Use WebSocket connections for real-time voice interaction
- Support multiple concurrent voice sessions
- Implement proper authentication and authorization
- Handle voice data securely and respect privacy
- Support multiple languages and accents
- Implement rate limiting for voice API calls
- Use structured logging for debugging voice issues

Voice Processing Architecture:
1. WebSocket endpoint for real-time voice streaming
2. HTTP endpoints for voice processing and analysis
3. AI integration with OpenAI and Claude APIs
4. Database operations with SQLAlchemy async
5. Real-time notifications and updates
6. File upload and processing for voice data

Security Considerations:
- Validate all voice input data
- Implement proper CORS policies
- Use HTTPS for all voice communications
- Rate limit voice processing requests
- Log voice processing for debugging (without sensitive data)
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import verify_token
from app.api.v1.api import api_router
from app.core.voice_processor import VoiceProcessor
from app.core.websocket_manager import WebSocketManager
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# WebSocket manager for real-time communication
websocket_manager = WebSocketManager()

# Voice processor for AI integration
voice_processor = VoiceProcessor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AI Voice Task Manager API...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize voice processor
    await voice_processor.initialize()
    
    logger.info("AI Voice Task Manager API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Voice Task Manager API...")
    await voice_processor.cleanup()
    await engine.dispose()
    logger.info("AI Voice Task Manager API shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="AI Voice Task Manager API",
    description="Revolutionary AI-powered voice-controlled task and project manager",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "AI Voice Task Manager API"
    }

# WebSocket endpoint for real-time voice communication
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time voice communication"""
    await websocket_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "voice_input":
                await handle_voice_input(websocket, user_id, message)
            elif message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.utcnow().isoformat()}))
            else:
                logger.warning(f"Unknown message type: {message.get('type')}")
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)
        logger.info(f"WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        websocket_manager.disconnect(user_id)

async def handle_voice_input(websocket: WebSocket, user_id: str, message: Dict[str, Any]):
    """Handle voice input from WebSocket"""
    try:
        audio_data = message.get("audio_data")
        session_id = message.get("session_id")
        
        if not audio_data:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "No audio data provided"
            }))
            return
        
        # Process voice input
        logger.info(f"Processing voice input for user {user_id}, session {session_id}")
        
        # Send processing status
        await websocket.send_text(json.dumps({
            "type": "voice_processing",
            "session_id": session_id,
            "status": "processing"
        }))
        
        # Process with AI
        result = await voice_processor.process_voice(audio_data, user_id, session_id)
        
        # Send result back
        await websocket.send_text(json.dumps({
            "type": "voice_response",
            "session_id": session_id,
            "result": result
        }))
        
        logger.info(f"Voice processing completed for user {user_id}, session {session_id}")
        
    except Exception as e:
        logger.error(f"Error processing voice input for user {user_id}: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Failed to process voice input",
            "session_id": message.get("session_id")
        }))

# Broadcast endpoint for notifications
@app.post("/api/broadcast")
async def broadcast_message(message: Dict[str, Any], current_user: str = Depends(get_current_user)):
    """Broadcast message to all connected clients"""
    try:
        await websocket_manager.broadcast(message)
        return {"status": "success", "message": "Message broadcasted"}
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast message")

# Voice processing endpoint
@app.post("/api/voice/process")
async def process_voice_endpoint(
    audio_data: str,
    session_id: str = None,
    current_user: str = Depends(get_current_user)
):
    """Process voice input and return AI response"""
    try:
        result = await voice_processor.process_voice(audio_data, current_user, session_id)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Voice analysis endpoint
@app.post("/api/voice/analyze")
async def analyze_voice_endpoint(
    audio_data: str,
    current_user: str = Depends(get_current_user)
):
    """Analyze voice input for intent and entities"""
    try:
        result = await voice_processor.analyze_voice(audio_data, current_user)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Voice analysis error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Get available voice commands
@app.get("/api/voice/commands")
async def get_voice_commands(current_user: str = Depends(get_current_user)):
    """Get available voice commands"""
    commands = [
        {
            "id": "1",
            "command": "Create task",
            "description": "Create a new task with voice input",
            "category": "task",
            "examples": [
                "Create a task to buy groceries",
                "Add a new task for the meeting tomorrow",
                "Create task: follow up with client"
            ],
            "enabled": True
        },
        {
            "id": "2",
            "command": "Create project",
            "description": "Create a new project",
            "category": "project",
            "examples": [
                "Create a new project called Website Redesign",
                "Start a project for Q4 planning",
                "Create project: Marketing Campaign"
            ],
            "enabled": True
        },
        {
            "id": "3",
            "command": "Mark task complete",
            "description": "Mark a task as completed",
            "category": "task",
            "examples": [
                "Mark the grocery shopping task as complete",
                "Complete the meeting preparation task",
                "Mark task done: client follow up"
            ],
            "enabled": True
        },
        {
            "id": "4",
            "command": "Show tasks",
            "description": "Display all tasks or filtered tasks",
            "category": "navigation",
            "examples": [
                "Show all my tasks",
                "Show pending tasks",
                "Show tasks for today"
            ],
            "enabled": True
        },
        {
            "id": "5",
            "command": "Show projects",
            "description": "Display all projects or project details",
            "category": "navigation",
            "examples": [
                "Show all projects",
                "Show active projects",
                "Show project status for Website Redesign"
            ],
            "enabled": True
        },
        {
            "id": "6",
            "command": "Assign task",
            "description": "Assign a task to a team member",
            "category": "task",
            "examples": [
                "Assign the design task to Sarah",
                "Give the coding task to John",
                "Assign task to David: review the proposal"
            ],
            "enabled": True
        },
        {
            "id": "7",
            "command": "Set priority",
            "description": "Set priority level for a task",
            "category": "task",
            "examples": [
                "Set high priority for the urgent task",
                "Make the client meeting urgent priority",
                "Set priority low for the documentation task"
            ],
            "enabled": True
        },
        {
            "id": "8",
            "command": "Add due date",
            "description": "Set a due date for a task",
            "category": "task",
            "examples": [
                "Set due date for the report to next Friday",
                "Add due date: finish the design by tomorrow",
                "Set deadline for the project to end of month"
            ],
            "enabled": True
        }
    ]
    
    return {
        "success": True,
        "data": commands
    }

# Voice feedback endpoint
@app.post("/api/voice/feedback")
async def submit_voice_feedback(
    feedback: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """Submit feedback for voice processing"""
    try:
        # Store feedback for improving voice recognition
        logger.info(f"Voice feedback from user {current_user}: {feedback}")
        return {
            "success": True,
            "message": "Feedback submitted successfully"
        }
    except Exception as e:
        logger.error(f"Voice feedback error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
