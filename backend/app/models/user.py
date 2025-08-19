"""
User model for the Voice AI Task Manager.

This model includes user authentication, voice preferences, and profile information
for the voice-controlled task management system.
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class User(Base):
    """User model with voice preferences and authentication."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    name = Column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    
    # Voice preferences and settings
    voice_preferences = Column(JSON, default={
        "language": "en-US",
        "speed": 1.0,
        "pitch": 1.0,
        "volume": 1.0,
        "auto_transcribe": True,
        "voice_commands_enabled": True,
        "confidence_threshold": 0.7,
        "voice_feedback_enabled": True,
        "accessibility_mode": False
    })
    
    # User status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tasks = relationship("Task", back_populates="created_by_user", foreign_keys="Task.created_by")
    assigned_tasks = relationship("Task", back_populates="assigned_user", foreign_keys="Task.assigned_to")
    projects = relationship("Project", back_populates="created_by_user", foreign_keys="Project.created_by")
    project_memberships = relationship("ProjectMember", back_populates="user")
    voice_sessions = relationship("VoiceSession", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
    
    @property
    def voice_language(self) -> str:
        """Get user's preferred voice language."""
        return self.voice_preferences.get("language", "en-US")
    
    @property
    def voice_confidence_threshold(self) -> float:
        """Get user's voice confidence threshold."""
        return self.voice_preferences.get("confidence_threshold", 0.7)
    
    @property
    def voice_commands_enabled(self) -> bool:
        """Check if voice commands are enabled for user."""
        return self.voice_preferences.get("voice_commands_enabled", True)
    
    def update_voice_preferences(self, preferences: dict):
        """Update user's voice preferences."""
        current_prefs = self.voice_preferences or {}
        current_prefs.update(preferences)
        self.voice_preferences = current_prefs
    
    def get_voice_preference(self, key: str, default=None):
        """Get a specific voice preference value."""
        return self.voice_preferences.get(key, default) if self.voice_preferences else default
