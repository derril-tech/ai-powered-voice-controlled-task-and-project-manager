"""
Notification model for the Voice AI Task Manager.

This model handles real-time notifications, alerts, and user communication
for the voice-controlled task management system.
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class NotificationType(str, enum.Enum):
    """Notification type enumeration."""
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_ASSIGNED = "task_assigned"
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_MEMBER_ADDED = "project_member_added"
    VOICE_COMMAND_PROCESSED = "voice_command_processed"
    VOICE_COMMAND_FAILED = "voice_command_failed"
    SYSTEM_ALERT = "system_alert"
    REMINDER = "reminder"


class NotificationPriority(str, enum.Enum):
    """Notification priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """Notification model for real-time alerts and user communication."""
    
    __tablename__ = "notifications"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Notification relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Notification information
    type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM, nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Notification status
    read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notification data
    data = Column(JSON, default={
        "task_id": None,
        "project_id": None,
        "voice_session_id": None,
        "voice_command_id": None,
        "action_url": None,
        "icon": None,
        "color": None
    })
    
    # Voice metadata for voice-related notifications
    voice_metadata = Column(JSON, default={
        "created_via_voice": False,
        "transcription": None,
        "intent": None,
        "confidence_score": None,
        "processing_time": None
    })
    
    # Notification metadata
    metadata = Column(JSON, default={
        "source": "system",  # system, voice, user
        "category": "general",
        "tags": [],
        "expires_at": None,
        "retry_count": 0
    })
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type}', user_id={self.user_id})>"
    
    @property
    def is_read(self) -> bool:
        """Check if notification is read."""
        return self.read
    
    @property
    def is_urgent(self) -> bool:
        """Check if notification is urgent priority."""
        return self.priority == NotificationPriority.URGENT
    
    @property
    def is_high_priority(self) -> bool:
        """Check if notification is high or urgent priority."""
        return self.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT]
    
    @property
    def created_via_voice(self) -> bool:
        """Check if notification was created via voice command."""
        return self.voice_metadata.get("created_via_voice", False) if self.voice_metadata else False
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.read = True
        self.read_at = func.now()
    
    def mark_as_unread(self):
        """Mark notification as unread."""
        self.read = False
        self.read_at = None
    
    def update_data(self, new_data: dict):
        """Update notification data."""
        current_data = self.data or {}
        current_data.update(new_data)
        self.data = current_data
    
    def update_voice_metadata(self, metadata: dict):
        """Update notification's voice metadata."""
        current_metadata = self.voice_metadata or {}
        current_metadata.update(metadata)
        self.voice_metadata = current_metadata
    
    def get_action_url(self) -> str:
        """Get the action URL for this notification."""
        return self.data.get("action_url", "") if self.data else ""
    
    def get_icon(self) -> str:
        """Get the icon for this notification."""
        return self.data.get("icon", "🔔") if self.data else "🔔"
    
    def get_color(self) -> str:
        """Get the color for this notification."""
        return self.data.get("color", "#3B82F6") if self.data else "#3B82F6"
    
    def is_expired(self) -> bool:
        """Check if notification has expired."""
        if not self.metadata or not self.metadata.get("expires_at"):
            return False
        from datetime import datetime, timezone
        expires_at = datetime.fromisoformat(self.metadata["expires_at"].replace('Z', '+00:00'))
        return datetime.now(timezone.utc) > expires_at
    
    def should_retry(self) -> bool:
        """Check if notification should be retried."""
        max_retries = 3
        current_retries = self.metadata.get("retry_count", 0) if self.metadata else 0
        return current_retries < max_retries
    
    def increment_retry_count(self):
        """Increment retry count."""
        current_metadata = self.metadata or {}
        current_metadata["retry_count"] = current_metadata.get("retry_count", 0) + 1
        self.metadata = current_metadata
    
    @classmethod
    def create_task_notification(cls, user_id: str, task_id: str, notification_type: NotificationType, 
                                title: str, message: str, priority: NotificationPriority = NotificationPriority.MEDIUM):
        """Create a task-related notification."""
        return cls(
            user_id=user_id,
            type=notification_type,
            priority=priority,
            title=title,
            message=message,
            data={
                "task_id": task_id,
                "action_url": f"/tasks/{task_id}",
                "icon": "📋",
                "color": "#10B981"
            }
        )
    
    @classmethod
    def create_project_notification(cls, user_id: str, project_id: str, notification_type: NotificationType,
                                   title: str, message: str, priority: NotificationPriority = NotificationPriority.MEDIUM):
        """Create a project-related notification."""
        return cls(
            user_id=user_id,
            type=notification_type,
            priority=priority,
            title=title,
            message=message,
            data={
                "project_id": project_id,
                "action_url": f"/projects/{project_id}",
                "icon": "📊",
                "color": "#3B82F6"
            }
        )
    
    @classmethod
    def create_voice_notification(cls, user_id: str, voice_session_id: str, voice_command_id: str,
                                 notification_type: NotificationType, title: str, message: str,
                                 voice_metadata: dict = None):
        """Create a voice-related notification."""
        return cls(
            user_id=user_id,
            type=notification_type,
            priority=NotificationPriority.MEDIUM,
            title=title,
            message=message,
            data={
                "voice_session_id": voice_session_id,
                "voice_command_id": voice_command_id,
                "action_url": "/voice-commands",
                "icon": "🎤",
                "color": "#8B5CF6"
            },
            voice_metadata=voice_metadata or {}
        )
    
    @classmethod
    def create_reminder_notification(cls, user_id: str, title: str, message: str,
                                    scheduled_at: DateTime, task_id: str = None, project_id: str = None):
        """Create a reminder notification."""
        data = {
            "action_url": "/dashboard",
            "icon": "⏰",
            "color": "#F59E0B"
        }
        
        if task_id:
            data["task_id"] = task_id
            data["action_url"] = f"/tasks/{task_id}"
        
        if project_id:
            data["project_id"] = project_id
            data["action_url"] = f"/projects/{project_id}"
        
        return cls(
            user_id=user_id,
            type=NotificationType.REMINDER,
            priority=NotificationPriority.HIGH,
            title=title,
            message=message,
            scheduled_at=scheduled_at,
            data=data
        )
