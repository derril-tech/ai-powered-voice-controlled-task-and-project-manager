# Backend Directory - Voice AI FastAPI Backend

## 🎯 Purpose
This directory contains the FastAPI backend for the voice-controlled task manager. The backend handles voice processing, AI integration, real-time communication, and data management.

## 📁 Backend Structure

### Core Application Files
- `main.py` - FastAPI application entry point with WebSocket support
- `requirements.txt` - Python dependencies for voice AI processing
- `alembic.ini` - Database migration configuration
- `docker-compose.yml` - Local development environment setup

### Planned Directory Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── project.py
│   │   └── voice.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── project.py
│   │   └── voice.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   ├── projects.py
│   │   └── voice.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── voice_processor.py
│   │   ├── ai_integration.py
│   │   ├── notification.py
│   │   └── file_upload.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── voice_utils.py
│   │   └── helpers.py
│   └── websockets/
│       ├── __init__.py
│       └── voice_handler.py
├── tests/
│   ├── __init__.py
│   ├── test_voice_processing.py
│   ├── test_ai_integration.py
│   └── test_api.py
├── alembic/
│   ├── versions/
│   └── env.py
└── logs/
    └── voice.log
```

## 🎤 Voice Processing Architecture

### For Claude Code When Implementing Backend:

1. **Voice Processing Pipeline**
   - Audio capture and preprocessing
   - Speech-to-text conversion with multiple AI providers
   - Intent recognition and entity extraction
   - Action execution and response generation
   - Real-time feedback via WebSocket

2. **AI Integration Strategy**
   - OpenAI GPT-4 for general voice understanding
   - Claude API for complex reasoning tasks
   - LangChain for orchestration and context management
   - Fallback mechanisms for API failures

3. **Real-time Communication**
   - WebSocket connections for live voice streaming
   - Event-driven architecture for voice commands
   - Connection management and error recovery
   - Scalable WebSocket handling

## 🔧 Implementation Patterns

### Voice Processing Service Pattern:
```python
class VoiceProcessor:
    def __init__(self):
        self.openai_client = OpenAI()
        self.claude_client = Anthropic()
        self.langchain_chain = self._setup_langchain()
    
    async def process_voice_command(self, audio_data: bytes, user_id: str) -> VoiceProcessingResult:
        """Process voice command with AI integration"""
        try:
            # 1. Convert audio to text
            transcription = await self._speech_to_text(audio_data)
            
            # 2. Extract intent and entities
            intent_result = await self._extract_intent(transcription)
            
            # 3. Execute action
            action_result = await self._execute_action(intent_result, user_id)
            
            # 4. Generate response
            response = await self._generate_response(action_result)
            
            return VoiceProcessingResult(
                success=True,
                transcription=transcription,
                intent=intent_result.intent,
                confidence=intent_result.confidence,
                response=response
            )
        except Exception as e:
            logger.error(f"Voice processing failed: {e}")
            return VoiceProcessingResult(success=False, error=str(e))
```

### WebSocket Handler Pattern:
```python
class VoiceWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_voice_feedback(self, user_id: str, feedback: VoiceProcessingResult):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(feedback.dict())
```

## 🗄️ Database Design

### Voice-Specific Models:
```python
class VoiceSession(Base):
    __tablename__ = "voice_sessions"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    commands_processed = Column(Integer, default=0)
    total_duration = Column(Float, default=0.0)
    status = Column(Enum("active", "ended", "error"))
    
    # Voice processing metadata
    language = Column(String(10))
    confidence_avg = Column(Float)
    error_count = Column(Integer, default=0)

class VoiceCommand(Base):
    __tablename__ = "voice_commands"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID, ForeignKey("voice_sessions.id"))
    command_text = Column(Text)
    intent = Column(String(100))
    confidence = Column(Float)
    entities = Column(JSON)
    processing_time = Column(Float)
    success = Column(Boolean)
    error_message = Column(Text, nullable=True)
```

## 🔒 Security Implementation

### Voice Data Security:
```python
class VoiceSecurityMiddleware:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.encryption = VoiceEncryption()
    
    async def validate_voice_request(self, request: Request) -> bool:
        """Validate voice processing request"""
        # Rate limiting
        if not await self.rate_limiter.check_limit(request.client.host):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Audio validation
        if not self._validate_audio_format(request):
            raise HTTPException(status_code=400, detail="Invalid audio format")
        
        return True
    
    def _validate_audio_format(self, request: Request) -> bool:
        """Validate audio format and size"""
        # Implementation for audio validation
        pass
```

## 🧪 Testing Strategy

### Voice Processing Tests:
```python
class TestVoiceProcessing:
    @pytest.fixture
    def voice_processor(self):
        return VoiceProcessor()
    
    @pytest.mark.asyncio
    async def test_voice_command_processing(self, voice_processor):
        """Test complete voice command processing pipeline"""
        audio_data = self._generate_test_audio()
        result = await voice_processor.process_voice_command(audio_data, "test_user")
        
        assert result.success is True
        assert result.transcription is not None
        assert result.confidence > 0.8
    
    @pytest.mark.asyncio
    async def test_voice_error_handling(self, voice_processor):
        """Test error handling for invalid voice input"""
        invalid_audio = b"invalid_audio_data"
        result = await voice_processor.process_voice_command(invalid_audio, "test_user")
        
        assert result.success is False
        assert result.error is not None
```

## 🚀 Performance Optimization

### Voice Processing Optimization:
- Implement audio caching for repeated commands
- Use async processing for non-blocking operations
- Optimize AI API calls with batching
- Implement connection pooling for database
- Use Redis for session management and caching

### Monitoring and Logging:
```python
import structlog

logger = structlog.get_logger()

class VoiceProcessingMetrics:
    def __init__(self):
        self.processing_times = []
        self.error_counts = {}
        self.confidence_scores = []
    
    def record_processing_time(self, duration: float):
        self.processing_times.append(duration)
        logger.info("Voice processing time recorded", duration=duration)
    
    def record_error(self, error_type: str):
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        logger.error("Voice processing error", error_type=error_type)
```

## 📝 API Documentation

### OpenAPI/Swagger Integration:
```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Voice AI Task Manager API",
    description="AI-powered voice-controlled task and project management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Voice AI Task Manager API",
        version="1.0.0",
        description="Complete API for voice-controlled task management",
        routes=app.routes,
    )
    
    # Add voice-specific documentation
    openapi_schema["info"]["x-voice-features"] = [
        "Real-time voice processing",
        "AI-powered intent recognition",
        "WebSocket communication",
        "Multi-language support"
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

## 🔄 Deployment Configuration

### Docker Configuration:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for voice processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

**Remember**: The backend is the core of the voice AI system. Every endpoint and service should be designed with voice processing, real-time communication, and AI integration in mind.
