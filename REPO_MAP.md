# Repository Map - AI-Powered Voice-Controlled Task & Project Manager

## 🗂️ Complete Project Structure

```
ai-powered-voice-controlled-task-and-project-manager/
├── 📁 Frontend (Next.js 14 + TypeScript)
│   ├── 📄 package.json                    # Dependencies and scripts
│   ├── 📄 next.config.js                  # Next.js configuration
│   ├── 📄 tailwind.config.js              # Tailwind CSS with voice-specific styles
│   ├── 📄 postcss.config.js               # PostCSS configuration
│   ├── 📄 tsconfig.json                   # TypeScript configuration
│   ├── 📄 .env.example                    # Environment variables template
│   │
│   ├── 📁 app/                            # Next.js App Router
│   │   ├── 📄 layout.tsx                  # Root layout with theme provider
│   │   ├── 📄 page.tsx                    # Landing page
│   │   ├── 📄 globals.css                 # Global styles
│   │   └── 📁 dashboard/
│   │       └── 📄 page.tsx                # Main dashboard with voice interface
│   │
│   ├── 📁 components/                     # React components
│   │   ├── 📄 VoiceRecorder.tsx           # Main voice recording interface
│   │   ├── 📄 TaskList.tsx                # Task display with voice interaction
│   │   ├── 📄 ProjectDashboard.tsx        # Project overview with voice commands
│   │   ├── 📄 VoiceCommands.tsx           # Available commands display
│   │   ├── 📄 NotificationCenter.tsx      # Real-time notifications
│   │   ├── 📄 ThemeProvider.tsx           # Dark/light mode management
│   │   └── 📄 README.md                   # Component development guide
│   │
│   ├── 📁 hooks/                          # Custom React hooks
│   │   └── 📄 useVoiceRecorder.ts         # Voice recording and processing hook
│   │
│   ├── 📁 lib/                            # Utility libraries
│   │   ├── 📄 store.ts                    # Zustand state management
│   │   ├── 📄 api.ts                      # API client with voice endpoints
│   │   └── 📄 utils.ts                    # Utility functions
│   │
│   ├── 📁 types/                          # TypeScript type definitions
│   │   └── 📄 index.ts                    # All shared types
│   │
│   └── 📁 tests/                          # Testing files
│       ├── 📁 unit/                       # Unit tests
│       ├── 📁 integration/                # Integration tests
│       └── 📁 e2e/                        # End-to-end tests
│
├── 📁 backend/                            # FastAPI Backend
│   ├── 📄 main.py                         # FastAPI application entry point
│   ├── 📄 requirements.txt                # Python dependencies
│   ├── 📄 .env.example                    # Environment variables template
│   ├── 📄 README.md                       # Backend development guide
│   │
│   ├── 📁 app/                            # Main application package
│   │   ├── 📄 __init__.py                 # Package initialization
│   │   ├── 📄 config.py                   # Configuration settings
│   │   ├── 📄 database.py                 # Database connection setup
│   │   │
│   │   ├── 📁 models/                     # SQLAlchemy database models
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 user.py                 # User model with voice preferences
│   │   │   ├── 📄 task.py                 # Task model with voice metadata
│   │   │   ├── 📄 project.py              # Project model
│   │   │   └── 📄 voice.py                # Voice session and command models
│   │   │
│   │   ├── 📁 schemas/                    # Pydantic validation schemas
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 user.py                 # User request/response schemas
│   │   │   ├── 📄 task.py                 # Task request/response schemas
│   │   │   ├── 📄 project.py              # Project request/response schemas
│   │   │   └── 📄 voice.py                # Voice processing schemas
│   │   │
│   │   ├── 📁 api/                        # FastAPI route handlers
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 auth.py                 # Authentication endpoints
│   │   │   ├── 📄 tasks.py                # Task management endpoints
│   │   │   ├── 📄 projects.py             # Project management endpoints
│   │   │   └── 📄 voice.py                # Voice processing endpoints
│   │   │
│   │   ├── 📁 services/                   # Business logic services
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 voice_processor.py      # Core voice processing logic
│   │   │   ├── 📄 ai_integration.py       # OpenAI/Claude integration
│   │   │   ├── 📄 notification.py         # Email notification service
│   │   │   └── 📄 file_upload.py          # File upload service
│   │   │
│   │   ├── 📁 utils/                      # Utility functions
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 security.py             # JWT and security utilities
│   │   │   ├── 📄 voice_utils.py          # Voice processing utilities
│   │   │   └── 📄 helpers.py              # General helper functions
│   │   │
│   │   └── 📁 websockets/                 # WebSocket handlers
│   │       ├── 📄 __init__.py
│   │       └── 📄 voice_handler.py        # Real-time voice communication
│   │
│   ├── 📁 tests/                          # Backend tests
│   │   ├── 📁 unit/                       # Unit tests
│   │   ├── 📁 integration/                # Integration tests
│   │   └── 📁 e2e/                        # End-to-end tests
│   │
│   ├── 📁 alembic/                        # Database migrations
│   │   ├── 📄 env.py                      # Alembic environment
│   │   └── 📁 versions/                   # Migration files
│   │
│   └── 📁 logs/                           # Application logs
│       └── 📄 voice.log                   # Voice processing logs
│
├── 📁 infrastructure/                     # Deployment and infrastructure
│   ├── 📄 docker-compose.yml              # Local development setup
│   ├── 📄 Dockerfile                      # Backend container
│   ├── 📄 Dockerfile.frontend             # Frontend container
│   └── 📄 nginx.conf                      # Nginx configuration
│
├── 📁 docs/                               # Documentation
│   ├── 📄 API_SPEC.md                     # Complete API specification
│   ├── 📄 DEPLOYMENT.md                   # Deployment instructions
│   └── 📄 TESTING.md                      # Testing guidelines
│
├── 📄 README.md                           # Main project documentation
├── 📄 CLAUDE_INSTRUCTIONS.md              # Claude Code instructions
├── 📄 DEVELOPMENT_GUIDE.md                # Development workflow guide
├── 📄 VOICE_CONFIG.md                     # Voice AI configuration
├── 📄 CLAUDE.md                           # Claude-specific guidance
└── 📄 .env.example                        # Environment variables template
```

## 🎯 **Key Implementation Files for Claude Code**

### **Frontend Core Files**
- **`app/dashboard/page.tsx`**: Main dashboard with voice interface integration
- **`components/VoiceRecorder.tsx`**: Core voice recording component with real-time feedback
- **`hooks/useVoiceRecorder.ts`**: Voice processing hook with WebSocket integration
- **`lib/store.ts`**: Zustand store for voice session and state management
- **`lib/api.ts`**: API client with voice processing endpoints
- **`types/index.ts`**: Complete TypeScript type definitions

### **Backend Core Files**
- **`main.py`**: FastAPI application with WebSocket endpoints
- **`app/services/voice_processor.py`**: Core voice processing pipeline
- **`app/services/ai_integration.py`**: OpenAI and Claude API integration
- **`app/websockets/voice_handler.py`**: Real-time voice communication
- **`app/models/voice.py`**: Voice session and command database models
- **`app/api/voice.py`**: Voice processing API endpoints

### **Configuration Files**
- **`tailwind.config.js`**: Voice-specific styling configuration
- **`tsconfig.json`**: TypeScript configuration with path aliases
- **`requirements.txt`**: Python dependencies for voice AI
- **`docker-compose.yml`**: Complete development environment

## 🔧 **Implementation Notes for Claude Code**

### **Voice Processing Pipeline**
1. **Frontend**: `VoiceRecorder.tsx` captures audio via MediaRecorder API
2. **WebSocket**: Real-time streaming to backend via `useVoiceRecorder.ts`
3. **Backend**: `voice_processor.py` processes audio with AI integration
4. **Response**: WebSocket sends processed results back to frontend
5. **UI Update**: Zustand store updates UI with voice command results

### **AI Integration Points**
- **OpenAI GPT-4**: General voice understanding and intent recognition
- **Claude API**: Complex reasoning and advanced task processing
- **LangChain**: Orchestration and context management
- **pgvector**: Vector storage for voice embeddings and semantic search

### **Real-time Communication**
- **WebSocket Endpoint**: `/ws/{user_id}` for live voice streaming
- **Message Types**: voice_input, voice_response, task_update, notification
- **Connection Management**: Automatic reconnection and error handling
- **Session Tracking**: Voice session state management

### **Database Schema**
- **Users**: Voice preferences and authentication
- **Tasks**: Voice metadata and processing history
- **Projects**: Team collaboration and voice commands
- **Voice Sessions**: Real-time session tracking and analytics

### **Security Implementation**
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Voice API call limits and protection
- **Input Validation**: Audio format and size validation
- **CORS Configuration**: Secure cross-origin communication

## 🚀 **Development Workflow**

### **Frontend Development**
1. **Component Creation**: Follow patterns in `components/README.md`
2. **Voice Integration**: Use `useVoiceRecorder.ts` hook
3. **State Management**: Update Zustand store in `lib/store.ts`
4. **Type Safety**: Add types to `types/index.ts`
5. **Testing**: Unit tests for voice components

### **Backend Development**
1. **API Endpoints**: Add routes in `app/api/` directory
2. **Voice Processing**: Extend `voice_processor.py` service
3. **Database Models**: Update models in `app/models/`
4. **WebSocket Handlers**: Modify `voice_handler.py`
5. **Testing**: Integration tests for voice endpoints

### **Voice Feature Development**
1. **Command Patterns**: Update `VOICE_CONFIG.md`
2. **Intent Recognition**: Extend AI integration in `ai_integration.py`
3. **UI Feedback**: Add voice feedback components
4. **Error Handling**: Implement graceful error recovery
5. **Documentation**: Update API specification

## 📊 **Monitoring and Analytics**

### **Voice Metrics Tracking**
- **Processing Time**: Voice command processing duration
- **Accuracy**: Speech recognition confidence scores
- **Usage Patterns**: Popular commands and user behavior
- **Error Rates**: Voice processing failure tracking
- **Performance**: Real-time response times

### **Logging and Debugging**
- **Structured Logging**: Voice processing events and errors
- **WebSocket Monitoring**: Connection status and message flow
- **AI API Monitoring**: OpenAI and Claude API usage
- **Database Performance**: Query optimization and indexing
- **User Experience**: Voice interaction success rates

## 🔒 **Security and Privacy**

### **Voice Data Protection**
- **Audio Encryption**: Secure transmission and storage
- **Transcription Privacy**: Sensitive data handling
- **Session Security**: Secure WebSocket connections
- **Access Control**: User authentication and authorization
- **Data Retention**: Configurable voice data retention policies

### **Compliance and Standards**
- **GDPR Compliance**: User data protection and privacy
- **WCAG 2.1 AA**: Accessibility standards for voice interface
- **Security Best Practices**: OWASP guidelines implementation
- **API Security**: Rate limiting and input validation
- **Error Handling**: Secure error messages and logging

---

**Note**: This repository map provides Claude Code with a complete understanding of the voice AI application structure, implementation patterns, and development workflow. All files are designed to work together seamlessly for a production-ready voice-controlled task management system.
