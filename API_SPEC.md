# API Specification - AI-Powered Voice-Controlled Task & Project Manager

## 🎯 **API Overview**

**Base URL**: `https://api.voice-task-manager.com/v1`  
**WebSocket URL**: `wss://api.voice-task-manager.com/ws/{user_id}`  
**Authentication**: JWT Bearer Token  
**Content-Type**: `application/json`  
**Voice Processing**: Real-time WebSocket communication with audio streaming

## 🔐 **Authentication**

### **JWT Token Format**
```json
{
  "Authorization": "Bearer <jwt_token>",
  "Content-Type": "application/json"
}
```

### **Token Structure**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": 1640995200,
  "iat": 1640908800,
  "voice_preferences": {
    "language": "en-US",
    "confidence_threshold": 0.7
  }
}
```

## 🎤 **Voice Processing Endpoints**

### **1. Voice Processing Pipeline**

#### **POST** `/api/voice/process`
Process voice audio and return AI response.

**Request Body:**
```json
{
  "audio_data": "base64_encoded_audio",
  "session_id": "uuid",
  "language": "en-US",
  "confidence_threshold": 0.7
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transcription": "Create a new task called buy groceries",
    "intent": "create_task",
    "confidence": 0.95,
    "entities": {
      "task_name": "buy groceries",
      "priority": "medium",
      "due_date": null
    },
    "response": "I've created a new task called 'buy groceries'",
    "processing_time": 1.2,
    "voice_metadata": {
      "language": "en-US",
      "audio_quality": "high",
      "background_noise": "low"
    }
  }
}
```

#### **POST** `/api/voice/analyze`
Analyze voice input for intent and entities without execution.

**Request Body:**
```json
{
  "transcription": "Mark the meeting task as complete",
  "context": {
    "current_project": "Q4 Planning",
    "user_preferences": {
      "language": "en-US"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "intent": "update_task",
    "confidence": 0.92,
    "entities": {
      "task_name": "meeting task",
      "status": "completed"
    },
    "suggested_actions": [
      "mark_task_complete",
      "update_task_status"
    ]
  }
}
```

#### **GET** `/api/voice/commands`
Get available voice commands and examples.

**Response:**
```json
{
  "success": true,
  "data": [
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
      "enabled": true,
      "confidence_threshold": 0.7
    },
    {
      "id": "2",
      "command": "Mark task complete",
      "description": "Mark a task as completed",
      "category": "task",
      "examples": [
        "Mark the grocery shopping task as complete",
        "Complete the meeting preparation task"
      ],
      "enabled": true,
      "confidence_threshold": 0.8
    }
  ]
}
```

#### **POST** `/api/voice/feedback`
Submit feedback for voice processing improvement.

**Request Body:**
```json
{
  "session_id": "uuid",
  "command_id": "1",
  "transcription": "Create task buy groceries",
  "intent": "create_task",
  "confidence": 0.95,
  "success": true,
  "user_feedback": "Perfect recognition",
  "processing_time": 1.2
}
```

## 🔄 **WebSocket Communication**

### **WebSocket Endpoint**
```
wss://api.voice-task-manager.com/ws/{user_id}
```

### **Message Types**

#### **1. Voice Input Message**
```json
{
  "type": "voice_input",
  "session_id": "uuid",
  "audio_data": "base64_encoded_audio",
  "timestamp": "2024-01-01T12:00:00Z",
  "metadata": {
    "language": "en-US",
    "audio_quality": "high"
  }
}
```

#### **2. Voice Response Message**
```json
{
  "type": "voice_response",
  "session_id": "uuid",
  "transcription": "Create a new task called buy groceries",
  "intent": "create_task",
  "confidence": 0.95,
  "response": "I've created a new task called 'buy groceries'",
  "entities": {
    "task_name": "buy groceries"
  },
  "timestamp": "2024-01-01T12:00:01Z"
}
```

#### **3. Task Update Message**
```json
{
  "type": "task_update",
  "task_id": "uuid",
  "action": "created",
  "task": {
    "id": "uuid",
    "title": "buy groceries",
    "status": "pending",
    "created_at": "2024-01-01T12:00:01Z"
  },
  "timestamp": "2024-01-01T12:00:01Z"
}
```

#### **4. Notification Message**
```json
{
  "type": "notification",
  "notification": {
    "id": "uuid",
    "type": "task_created",
    "title": "Task Created",
    "message": "New task 'buy groceries' has been created",
    "timestamp": "2024-01-01T12:00:01Z"
  }
}
```

#### **5. Error Message**
```json
{
  "type": "error",
  "session_id": "uuid",
  "error_code": "VOICE_PROCESSING_ERROR",
  "message": "Unable to process voice input",
  "suggestions": [
    "Try speaking more clearly",
    "Check your microphone settings"
  ],
  "timestamp": "2024-01-01T12:00:01Z"
}
```

## 📋 **Task Management Endpoints**

### **GET** `/api/tasks`
Get user's tasks with filtering and pagination.

**Query Parameters:**
- `status`: Filter by status (pending, in_progress, completed, cancelled)
- `priority`: Filter by priority (low, medium, high, urgent)
- `project_id`: Filter by project
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid",
        "title": "Buy groceries",
        "description": "Weekly grocery shopping",
        "status": "pending",
        "priority": "medium",
        "due_date": "2024-01-05T00:00:00Z",
        "project_id": "uuid",
        "assigned_to": "uuid",
        "created_by": "uuid",
        "tags": ["shopping", "weekly"],
        "voice_metadata": {
          "original_audio_url": "https://storage.example.com/audio/uuid.wav",
          "transcription": "Create task buy groceries",
          "confidence_score": 0.95
        },
        "created_at": "2024-01-01T12:00:01Z",
        "updated_at": "2024-01-01T12:00:01Z"
      }
    ],
    "total": 50,
    "page": 1,
    "limit": 20,
    "total_pages": 3
  }
}
```

### **POST** `/api/tasks`
Create a new task.

**Request Body:**
```json
{
  "title": "Buy groceries",
  "description": "Weekly grocery shopping",
  "priority": "medium",
  "due_date": "2024-01-05T00:00:00Z",
  "project_id": "uuid",
  "assigned_to": "uuid",
  "tags": ["shopping", "weekly"],
  "voice_metadata": {
    "transcription": "Create task buy groceries",
    "confidence_score": 0.95
  }
}
```

### **PUT** `/api/tasks/{task_id}`
Update an existing task.

**Request Body:**
```json
{
  "title": "Buy groceries",
  "status": "completed",
  "priority": "high",
  "voice_metadata": {
    "transcription": "Mark task buy groceries as complete",
    "confidence_score": 0.92
  }
}
```

### **DELETE** `/api/tasks/{task_id}`
Delete a task.

**Response:**
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

## 📊 **Project Management Endpoints**

### **GET** `/api/projects`
Get user's projects.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Q4 Planning",
      "description": "Fourth quarter planning and strategy",
      "status": "active",
      "members": [
        {
          "user_id": "uuid",
          "role": "owner",
          "joined_at": "2024-01-01T00:00:00Z"
        }
      ],
      "created_by": "uuid",
      "color": "#3B82F6",
      "icon": "📊",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### **POST** `/api/projects`
Create a new project.

**Request Body:**
```json
{
  "name": "Q4 Planning",
  "description": "Fourth quarter planning and strategy",
  "color": "#3B82F6",
  "icon": "📊",
  "members": ["uuid1", "uuid2"]
}
```

## 👤 **User Management Endpoints**

### **GET** `/api/users/me`
Get current user profile.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "avatar": "https://storage.example.com/avatars/uuid.jpg",
    "voice_preferences": {
      "language": "en-US",
      "speed": 1.0,
      "pitch": 1.0,
      "volume": 1.0,
      "auto_transcribe": true,
      "voice_commands_enabled": true,
      "confidence_threshold": 0.7
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### **PUT** `/api/users/me/voice-preferences`
Update voice preferences.

**Request Body:**
```json
{
  "language": "en-US",
  "speed": 1.2,
  "pitch": 1.0,
  "volume": 0.8,
  "auto_transcribe": true,
  "voice_commands_enabled": true,
  "confidence_threshold": 0.8
}
```

## 📈 **Analytics Endpoints**

### **GET** `/api/analytics/voice`
Get voice processing analytics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_commands": 150,
    "successful_commands": 142,
    "average_confidence": 0.89,
    "most_used_commands": [
      {
        "command": "create_task",
        "count": 45
      },
      {
        "command": "mark_task_complete",
        "count": 32
      }
    ],
    "processing_time_stats": {
      "average": 1.2,
      "min": 0.8,
      "max": 3.5
    },
    "daily_usage": [
      {
        "date": "2024-01-01",
        "commands": 25
      }
    ]
  }
}
```

## 🔔 **Notification Endpoints**

### **GET** `/api/notifications`
Get user notifications.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "type": "task_assigned",
      "title": "Task Assigned",
      "message": "You have been assigned to 'Review proposal'",
      "read": false,
      "data": {
        "task_id": "uuid",
        "task_title": "Review proposal"
      },
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### **PUT** `/api/notifications/{notification_id}/read`
Mark notification as read.

**Response:**
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

## 🚨 **Error Responses**

### **Standard Error Format**
```json
{
  "success": false,
  "error": {
    "code": "VOICE_PROCESSING_ERROR",
    "message": "Unable to process voice input",
    "details": {
      "confidence": 0.3,
      "suggestions": [
        "Try speaking more clearly",
        "Check your microphone settings"
      ]
    },
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### **Common Error Codes**
- `AUTHENTICATION_ERROR`: Invalid or expired token
- `VOICE_PROCESSING_ERROR`: Voice processing failed
- `LOW_CONFIDENCE`: Speech recognition confidence too low
- `INVALID_AUDIO_FORMAT`: Unsupported audio format
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `TASK_NOT_FOUND`: Task not found
- `PROJECT_NOT_FOUND`: Project not found
- `PERMISSION_DENIED`: Insufficient permissions

## 🔒 **Security Headers**

### **Required Headers**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Request-ID: <unique_request_id>
X-Client-Version: 1.0.0
```

### **Rate Limiting**
- **Voice Processing**: 60 requests per minute per user
- **Task Operations**: 100 requests per minute per user
- **WebSocket Connections**: 10 concurrent connections per user

## 📊 **WebSocket Connection Management**

### **Connection Lifecycle**
1. **Connect**: Establish WebSocket connection with JWT token
2. **Authenticate**: Validate token and create voice session
3. **Stream Audio**: Send voice input messages
4. **Receive Responses**: Handle voice response messages
5. **Disconnect**: Clean up session and close connection

### **Heartbeat**
```json
{
  "type": "ping",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response:**
```json
{
  "type": "pong",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🎯 **Voice Processing Specifications**

### **Audio Format Requirements**
- **Format**: WAV, MP3, or WebM
- **Sample Rate**: 16kHz (optimal for speech recognition)
- **Channels**: Mono
- **Bit Depth**: 16-bit
- **Max Duration**: 30 seconds
- **Max Size**: 10MB

### **Voice Command Patterns**
- **Task Creation**: "Create task [task_name]"
- **Task Completion**: "Mark [task_name] as complete"
- **Task Assignment**: "Assign [task_name] to [user_name]"
- **Project Creation**: "Create project [project_name]"
- **Navigation**: "Show my tasks", "Go to dashboard"

### **Confidence Thresholds**
- **High Confidence**: ≥0.8 (execute immediately)
- **Medium Confidence**: 0.6-0.8 (ask for confirmation)
- **Low Confidence**: <0.6 (request clarification)

---

**Note**: This API specification provides Claude Code with complete understanding of the voice AI application's API structure, request/response formats, and voice processing requirements for seamless integration and development.
