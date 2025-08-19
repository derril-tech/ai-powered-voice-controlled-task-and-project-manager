# Claude Code Guidance - Voice AI Task Manager

## 🎯 **Direct Instructions for Claude Code**

### **Project Context**
You are working on an **AI-Powered Voice-Controlled Task & Project Manager** - a revolutionary voice-first productivity application that transforms natural speech into actionable tasks and project management commands. This is a production-ready, full-stack application using Next.js 14, FastAPI, and advanced AI integration.

### **Your Role**
As Claude Code, you are responsible for:
1. **Understanding the voice-first architecture** and implementing voice processing features
2. **Building responsive, accessible UI components** that work with voice interaction
3. **Implementing real-time WebSocket communication** for voice streaming
4. **Integrating AI services** (OpenAI GPT-4 + Claude API) for voice understanding
5. **Ensuring production-ready code** with proper error handling and security

## 🏗️ **Architecture Understanding**

### **Voice Processing Pipeline**
```
User Speech → Audio Capture → WebSocket Stream → AI Processing → Intent Recognition → Action Execution → Voice Response
```

### **Key Technologies**
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Zustand, WebSocket
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL + pgvector, Redis
- **AI**: OpenAI GPT-4, Claude API, LangChain
- **Voice**: MediaRecorder API, Web Speech API, Real-time streaming

### **Core Principles**
1. **Voice-First Design**: Every feature should work with voice interaction
2. **Real-time Communication**: WebSocket for live voice processing
3. **AI Integration**: Multiple AI models for robust voice understanding
4. **Accessibility**: WCAG 2.1 AA compliance for voice interface
5. **Production Ready**: Error handling, security, monitoring

## 🔧 **Implementation Guidelines**

### **When Creating Components**
1. **Always consider voice interaction** - every component should support voice commands
2. **Implement real-time feedback** - show voice processing status and confidence
3. **Use TypeScript strictly** - define comprehensive types for voice data
4. **Follow accessibility patterns** - ARIA labels, keyboard navigation, screen reader support
5. **Handle voice errors gracefully** - provide fallbacks and retry mechanisms

### **When Implementing Voice Features**
1. **Use the voice processing pipeline** defined in `hooks/useVoiceRecorder.ts`
2. **Integrate with WebSocket** for real-time communication
3. **Update Zustand store** for voice session state management
4. **Implement confidence scoring** and user feedback
5. **Add voice metadata** to all voice-created content

### **When Working with AI Integration**
1. **Use OpenAI GPT-4** for general voice understanding
2. **Use Claude API** for complex reasoning tasks
3. **Implement LangChain** for orchestration and context
4. **Add fallback mechanisms** for API failures
5. **Cache voice embeddings** in pgvector for semantic search

## 📁 **Key Files to Understand**

### **Frontend Core Files**
- **`components/VoiceRecorder.tsx`**: Main voice recording interface
- **`hooks/useVoiceRecorder.ts`**: Voice processing hook with WebSocket
- **`lib/store.ts`**: Zustand store for voice session management
- **`lib/api.ts`**: API client with voice endpoints
- **`types/index.ts`**: Complete TypeScript type definitions

### **Backend Core Files**
- **`main.py`**: FastAPI app with WebSocket endpoints
- **`app/services/voice_processor.py`**: Core voice processing logic
- **`app/services/ai_integration.py`**: AI service integration
- **`app/websockets/voice_handler.py`**: Real-time voice communication
- **`app/models/voice.py`**: Voice session and command models

### **Configuration Files**
- **`VOICE_CONFIG.md`**: Complete voice processing configuration
- **`API_SPEC.md`**: Detailed API specification
- **`REPO_MAP.md`**: Complete project structure
- **`DEVELOPMENT_GUIDE.md`**: Development workflow

## 🎤 **Voice Command Patterns**

### **Task Management Commands**
```typescript
// Create tasks
"Create a new task called [task_name]"
"Add task [task_name] for [project_name]"
"New task [task_name] with high priority"

// Update tasks
"Mark [task_name] as complete"
"Set priority of [task_name] to high"
"Assign [task_name] to [user_name]"

// Query tasks
"Show my pending tasks"
"What's my next task?"
"List tasks for [project_name]"
```

### **Project Management Commands**
```typescript
// Create projects
"Create a new project called [project_name]"
"Start project [project_name]"

// Manage projects
"Add [user_name] to [project_name]"
"Show status of [project_name]"
"Archive project [project_name]"
```

### **System Commands**
```typescript
// Navigation
"Go to dashboard"
"Show tasks"
"Open settings"

// Voice controls
"Start listening"
"Stop listening"
"Show available commands"
```

## 🔄 **Real-time Communication Patterns**

### **WebSocket Message Flow**
```typescript
// 1. Voice Input
{
  type: "voice_input",
  session_id: "uuid",
  audio_data: "base64_encoded_audio",
  timestamp: "2024-01-01T12:00:00Z"
}

// 2. Processing Status
{
  type: "voice_processing",
  session_id: "uuid",
  status: "processing"
}

// 3. Voice Response
{
  type: "voice_response",
  session_id: "uuid",
  transcription: "Create task buy groceries",
  intent: "create_task",
  confidence: 0.95,
  response: "I've created a new task called 'buy groceries'"
}

// 4. Task Update
{
  type: "task_update",
  task_id: "uuid",
  action: "created",
  task: { /* task data */ }
}
```

### **Error Handling**
```typescript
// Voice processing error
{
  type: "error",
  session_id: "uuid",
  error_code: "VOICE_PROCESSING_ERROR",
  message: "Unable to process voice input",
  suggestions: ["Try speaking more clearly", "Check microphone"]
}
```

## 🎯 **Development Workflow**

### **Adding New Voice Commands**
1. **Update `VOICE_CONFIG.md`** with new command patterns
2. **Extend `ai_integration.py`** for intent recognition
3. **Add UI components** for voice feedback
4. **Update WebSocket handlers** for new message types
5. **Add comprehensive tests** for voice scenarios

### **Implementing Voice Features**
1. **Define TypeScript types** in `types/index.ts`
2. **Create voice-enabled components** following patterns in `components/README.md`
3. **Update Zustand store** for voice state management
4. **Add API endpoints** for voice processing
5. **Implement error handling** and user feedback

### **Testing Voice Features**
1. **Unit tests** for voice processing logic
2. **Integration tests** for WebSocket communication
3. **E2E tests** for complete voice workflows
4. **Accessibility tests** for voice interface
5. **Performance tests** for real-time processing

## 🔒 **Security and Privacy**

### **Voice Data Protection**
- **Never log sensitive voice data** - only metadata and processing results
- **Encrypt audio transmission** - use HTTPS and secure WebSocket
- **Implement rate limiting** - prevent abuse of voice processing
- **Validate all input** - audio format, size, and content
- **User consent** - clear privacy policy for voice data

### **Authentication and Authorization**
- **JWT tokens** for secure authentication
- **Voice session management** with proper cleanup
- **User permissions** for voice features
- **Audit logging** for voice processing events

## 📊 **Performance Optimization**

### **Voice Processing Performance**
- **Target**: <2 seconds end-to-end voice processing
- **WebSocket**: <500ms real-time response
- **Database**: <100ms query response
- **Caching**: Redis for voice session data
- **CDN**: Static assets and voice feedback

### **Monitoring and Analytics**
- **Voice accuracy tracking** - confidence scores and user feedback
- **Processing time monitoring** - identify bottlenecks
- **Error rate tracking** - voice processing failures
- **Usage analytics** - popular commands and patterns
- **Performance metrics** - real-time response times

## 🚀 **Deployment Considerations**

### **Environment Setup**
- **PostgreSQL with pgvector** for voice embeddings
- **Redis** for session management and caching
- **Cloud storage** for audio files and voice data
- **AI API keys** for OpenAI and Claude integration
- **WebSocket support** for real-time communication

### **Production Configuration**
- **HTTPS/WSS** for secure voice communication
- **Rate limiting** for voice API endpoints
- **Monitoring** for voice processing performance
- **Backup strategies** for voice data
- **Scaling** for concurrent voice sessions

## 🎯 **Success Criteria**

### **Voice Recognition Accuracy**
- **Target**: >95% accuracy for clear speech
- **Graceful degradation** for unclear input
- **Context awareness** for better understanding
- **User feedback** for continuous improvement

### **User Experience**
- **Voice command success rate**: >90%
- **Error recovery rate**: >80%
- **Real-time feedback**: <500ms response
- **Accessibility compliance**: WCAG 2.1 AA

### **Technical Performance**
- **Voice processing**: <2 seconds end-to-end
- **WebSocket latency**: <500ms
- **Database queries**: <100ms
- **Uptime**: 99.9% availability

## 🔍 **Debugging and Troubleshooting**

### **Common Voice Issues**
1. **Low confidence scores**: Check audio quality and background noise
2. **Intent misclassification**: Review training data and context
3. **WebSocket disconnections**: Implement reconnection logic
4. **AI API failures**: Add fallback mechanisms
5. **Performance issues**: Monitor processing pipeline

### **Debug Tools**
- **Voice processing logs** in `logs/voice.log`
- **WebSocket connection monitoring**
- **AI API usage tracking**
- **Performance metrics dashboard**
- **User feedback collection**

---

**Remember**: This is a voice-first application. Every feature, component, and interaction should enhance the voice experience while maintaining traditional UI accessibility. Focus on creating a seamless, intelligent voice interface that makes task management effortless and natural.
