# Claude Code Instructions - AI-Powered Voice-Controlled Task & Project Manager

## 🎯 Project Overview
This is a production-ready, full-stack voice AI application that transforms natural speech into actionable tasks and project management commands. The system uses advanced AI models (OpenAI GPT-4 + Claude) to understand context, process voice input, and manage complex workflows.

## 🏗️ Architecture Decisions

### Frontend (Next.js 14 + TypeScript)
- **App Router**: Using Next.js 14 App Router for modern routing and server components
- **State Management**: Zustand for global state (lightweight, TypeScript-friendly)
- **Styling**: Tailwind CSS with custom design system for voice AI interface
- **Real-time**: WebSocket connections for live voice processing feedback
- **Accessibility**: WCAG 2.1 AA compliance for voice technology users

### Backend (FastAPI + Python)
- **Async First**: All database operations and API calls are async/await
- **ORM**: SQLAlchemy 2.0 with async support and pgvector for AI embeddings
- **Authentication**: JWT tokens with refresh mechanism
- **Voice Processing**: Custom pipeline integrating OpenAI + Claude APIs
- **Real-time**: WebSocket endpoints for live voice interaction

### Database (PostgreSQL + pgvector)
- **Vector Storage**: pgvector for storing voice embeddings and semantic search
- **Relationships**: Proper foreign keys and indexes for performance
- **Migrations**: Alembic for schema versioning

## 🔧 Implementation Guidelines

### For Claude Code When Adding Features:

1. **Voice Processing Priority**: Always consider voice input context when designing new features
2. **TypeScript First**: Define comprehensive types before implementing components
3. **Error Handling**: Implement graceful error handling for voice recognition failures
4. **Real-time Updates**: Use WebSocket connections for live voice feedback
5. **Accessibility**: Ensure all voice features work with screen readers
6. **Mobile-First**: Design for touch interfaces and mobile voice usage

### Code Quality Standards:
- Use TypeScript strict mode
- Implement proper error boundaries
- Add comprehensive JSDoc comments
- Follow ESLint + Prettier configuration
- Write unit tests for all voice processing logic
- Use semantic commit messages

### Security Considerations:
- Validate all voice input data
- Implement rate limiting for voice API calls
- Secure WebSocket connections
- Encrypt sensitive voice data
- Use environment variables for all secrets

## 📁 File Structure Guidelines

### Frontend Components:
- `components/` - Reusable UI components
- `hooks/` - Custom React hooks (especially voice-related)
- `lib/` - Utility functions and API clients
- `types/` - TypeScript type definitions
- `app/` - Next.js App Router pages

### Backend Structure:
- `models/` - SQLAlchemy database models
- `schemas/` - Pydantic validation schemas
- `api/` - FastAPI route handlers
- `services/` - Business logic and AI integrations
- `utils/` - Helper functions

## 🎤 Voice AI Integration Points

### Key Voice Features to Implement:
1. **Voice Command Recognition**: Parse natural language into structured commands
2. **Context Awareness**: Understand project context and user preferences
3. **Real-time Feedback**: Provide immediate voice responses
4. **Error Recovery**: Handle unclear voice input gracefully
5. **Multi-language Support**: Support multiple languages for voice commands

### Voice Processing Pipeline:
1. Audio capture → 2. Speech-to-text → 3. Intent recognition → 4. Action execution → 5. Voice response

## 🚀 Deployment Considerations

### Environment Variables:
- All AI API keys must be environment variables
- Database connection strings
- JWT secrets
- Cloud storage credentials

### Performance Optimization:
- Implement voice data caching
- Optimize database queries for voice search
- Use CDN for static assets
- Implement proper error monitoring

## 📝 Documentation Requirements

### For Each New Feature:
1. Update API documentation (OpenAPI/Swagger)
2. Add TypeScript type definitions
3. Update README.md with usage examples
4. Include voice command examples
5. Add unit tests with voice scenarios

## 🔄 Development Workflow

### When Adding New Voice Commands:
1. Define the command structure in `types/voice.ts`
2. Implement backend processing in `services/voice_processor.py`
3. Add frontend UI in appropriate component
4. Update WebSocket handlers for real-time feedback
5. Add comprehensive tests
6. Update documentation

### Testing Voice Features:
- Test with various accents and speech patterns
- Verify error handling for unclear input
- Test real-time performance
- Validate accessibility compliance

## 🎯 Success Metrics

### Voice Recognition Accuracy:
- Target: >95% accuracy for clear speech
- Graceful degradation for unclear input
- Context-aware error recovery

### Performance Targets:
- Voice processing: <2 seconds
- Real-time feedback: <500ms
- Database queries: <100ms

## 🛠️ Common Patterns

### Voice Command Structure:
```typescript
interface VoiceCommand {
  intent: 'create_task' | 'update_project' | 'get_status';
  entities: {
    task_name?: string;
    project_name?: string;
    due_date?: string;
    assignee?: string;
  };
  confidence: number;
  context?: ProjectContext;
}
```

### Error Handling Pattern:
```typescript
try {
  const result = await processVoiceCommand(audioData);
  return { success: true, data: result };
} catch (error) {
  logger.error('Voice processing failed', error);
  return { 
    success: false, 
    error: 'I didn\'t catch that. Could you repeat?',
    fallback: true 
  };
}
```

## 🔍 Debugging Voice Issues

### Common Problems:
1. **Low confidence scores**: Check audio quality and background noise
2. **Intent misclassification**: Review training data and context
3. **Real-time delays**: Check WebSocket connection and processing pipeline
4. **Accessibility issues**: Verify screen reader compatibility

### Debug Tools:
- Voice processing logs in `logs/voice.log`
- WebSocket connection monitoring
- Performance metrics in Prometheus
- Error tracking in structured logs

## 📚 Additional Resources

### Voice AI Best Practices:
- Design for conversational interfaces
- Provide clear feedback for all actions
- Implement progressive disclosure for complex commands
- Support both voice and text input as fallbacks

### Security Best Practices:
- Never log sensitive voice data
- Implement proper authentication for voice features
- Use HTTPS for all voice API calls
- Regular security audits of voice processing pipeline

---

**Remember**: This is a voice-first application. Every feature should be designed with voice interaction as the primary interface, with traditional UI as a secondary option.
