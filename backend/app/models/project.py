"""
Project models for the Voice AI Task Manager.

This module includes Project and ProjectMember models for team collaboration
and project management in the voice-controlled task management system.
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class ProjectStatus(str, enum.Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    ON_HOLD = "on_hold"


class ProjectMemberRole(str, enum.Enum):
    """Project member role enumeration."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Project(Base):
    """Project model for team collaboration and project management."""
    
    __tablename__ = "projects"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Project information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Project status and metadata
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    color = Column(String(7), default="#3B82F6")  # Hex color code
    icon = Column(String(10), default="📊")  # Emoji or icon
    
    # Project relationships
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Voice metadata
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
    created_by_user = relationship("User", back_populates="projects", foreign_keys=[created_by])
    tasks = relationship("Task", back_populates="project")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if project is active."""
        return self.status == ProjectStatus.ACTIVE
    
    @property
    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self.status == ProjectStatus.COMPLETED
    
    @property
    def created_via_voice(self) -> bool:
        """Check if project was created via voice command."""
        return self.voice_metadata.get("created_via_voice", False) if self.voice_metadata else False
    
    @property
    def voice_confidence_score(self) -> float:
        """Get voice confidence score."""
        return self.voice_metadata.get("confidence_score", 0.0) if self.voice_metadata else 0.0
    
    def update_voice_metadata(self, metadata: dict):
        """Update project's voice metadata."""
        current_metadata = self.voice_metadata or {}
        current_metadata.update(metadata)
        current_metadata["voice_update_count"] = current_metadata.get("voice_update_count", 0) + 1
        current_metadata["last_voice_update"] = func.now()
        self.voice_metadata = current_metadata
    
    def mark_completed(self, via_voice: bool = False, voice_metadata: dict = None):
        """Mark project as completed."""
        self.status = ProjectStatus.COMPLETED
        self.completed_at = func.now()
        
        if via_voice and voice_metadata:
            self.update_voice_metadata(voice_metadata)
    
    def get_member_count(self) -> int:
        """Get the number of project members."""
        return len(self.members)
    
    def get_task_count(self) -> int:
        """Get the number of tasks in this project."""
        return len(self.tasks)
    
    def get_completed_task_count(self) -> int:
        """Get the number of completed tasks in this project."""
        return len([task for task in self.tasks if task.is_completed])
    
    def get_progress_percentage(self) -> float:
        """Get project completion percentage based on tasks."""
        if not self.tasks:
            return 0.0
        completed = self.get_completed_task_count()
        total = self.get_task_count()
        return (completed / total) * 100 if total > 0 else 0.0


class ProjectMember(Base):
    """Project member model for team collaboration."""
    
    __tablename__ = "project_members"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Member relationships
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Member role and permissions
    role = Column(Enum(ProjectMemberRole), default=ProjectMemberRole.MEMBER, nullable=False)
    
    # Member status
    is_active = Column(Boolean, default=True)
    
    # Voice metadata for member addition
    voice_metadata = Column(JSON, default={
        "added_via_voice": False,
        "transcription": None,
        "intent": None,
        "confidence_score": None,
        "processing_time": None
    })
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")
    
    def __repr__(self):
        return f"<ProjectMember(project_id={self.project_id}, user_id={self.user_id}, role='{self.role}')>"
    
    @property
    def is_owner(self) -> bool:
        """Check if member is project owner."""
        return self.role == ProjectMemberRole.OWNER
    
    @property
    def is_admin(self) -> bool:
        """Check if member is project admin."""
        return self.role in [ProjectMemberRole.OWNER, ProjectMemberRole.ADMIN]
    
    @property
    def can_edit(self) -> bool:
        """Check if member can edit project."""
        return self.role in [ProjectMemberRole.OWNER, ProjectMemberRole.ADMIN, ProjectMemberRole.MEMBER]
    
    @property
    def added_via_voice(self) -> bool:
        """Check if member was added via voice command."""
        return self.voice_metadata.get("added_via_voice", False) if self.voice_metadata else False
    
    def update_voice_metadata(self, metadata: dict):
        """Update member's voice metadata."""
        current_metadata = self.voice_metadata or {}
        current_metadata.update(metadata)
        self.voice_metadata = current_metadata
