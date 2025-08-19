"""
Task model for the Voice AI Task Manager.

This model includes task information, voice metadata, and relationships
for the voice-controlled task management system.
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class TaskStatus(str, enum.Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    """Task model with voice metadata and task management."""
    
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Task information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Task status and priority
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    
    # Task relationships
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Task metadata
    due_date = Column(DateTime(timezone=True), nullable=True)
    tags = Column(ARRAY(String), default=[])
    
    # Voice metadata - stores information about voice creation/updates
    voice_metadata = Column(JSON, default={
        "created_via_voice": False,
        "original_audio_url": None,
        "transcription": None,
        "intent": None,
        "confidence_score": None,
        "processing_time": None,
        "language": None,
        "voice_command": None,
        "last_voice_update": None,
        "voice_update_count": 0
    })
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    created_by_user = relationship("User", back_populates="tasks", foreign_keys=[created_by])
    assigned_user = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to])
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date or self.is_completed:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.due_date
    
    @property
    def created_via_voice(self) -> bool:
        """Check if task was created via voice command."""
        return self.voice_metadata.get("created_via_voice", False) if self.voice_metadata else False
    
    @property
    def voice_confidence_score(self) -> float:
        """Get voice confidence score."""
        return self.voice_metadata.get("confidence_score", 0.0) if self.voice_metadata else 0.0
    
    def update_voice_metadata(self, metadata: dict):
        """Update task's voice metadata."""
        current_metadata = self.voice_metadata or {}
        current_metadata.update(metadata)
        current_metadata["voice_update_count"] = current_metadata.get("voice_update_count", 0) + 1
        current_metadata["last_voice_update"] = func.now()
        self.voice_metadata = current_metadata
    
    def mark_completed(self, via_voice: bool = False, voice_metadata: dict = None):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = func.now()
        
        if via_voice and voice_metadata:
            self.update_voice_metadata(voice_metadata)
    
    def get_voice_transcription(self) -> str:
        """Get the original voice transcription for this task."""
        return self.voice_metadata.get("transcription", "") if self.voice_metadata else ""
    
    def get_voice_intent(self) -> str:
        """Get the voice intent that created/updated this task."""
        return self.voice_metadata.get("intent", "") if self.voice_metadata else ""
