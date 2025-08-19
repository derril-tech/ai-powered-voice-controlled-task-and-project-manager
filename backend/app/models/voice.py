"""
Voice models for the Voice AI Task Manager.

This module includes models for voice sessions, commands, and analytics
to track and manage voice interactions in the task management system.
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, ForeignKey, Enum, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class VoiceSessionStatus(str, enum.Enum):
    """Voice session status enumeration."""
    ACTIVE = "active"
    IDLE = "idle"
    PAUSED = "paused"
    ENDED = "ended"
    ERROR = "error"


class VoiceCommandStatus(str, enum.Enum):
    """Voice command status enumeration."""
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VoiceSession(Base):
    """Voice session model for tracking voice interaction sessions."""
    
    __tablename__ = "voice_sessions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Session relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Session information
    status = Column(Enum(VoiceSessionStatus), default=VoiceSessionStatus.ACTIVE, nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Session metrics
    commands_processed = Column(Integer, default=0)
    total_duration = Column(Float, default=0.0)  # Duration in seconds
    error_count = Column(Integer, default=0)
    
    # Voice processing metadata
    language = Column(String(10), default="en-US")
    confidence_avg = Column(Float, default=0.0)
    audio_quality_score = Column(Float, default=0.0)
    background_noise_level = Column(Float, default=0.0)
    
    # Session metadata
    metadata = Column(JSON, default={
        "device_info": None,
        "browser_info": None,
        "connection_type": None,
        "audio_format": None,
        "sample_rate": None,
        "channels": None
    })
    
    # Timestamps
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="voice_sessions")
    commands = relationship("VoiceCommand", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VoiceSession(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == VoiceSessionStatus.ACTIVE
    
    @property
    def duration(self) -> float:
        """Get session duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (func.now() - self.start_time).total_seconds()
    
    @property
    def success_rate(self) -> float:
        """Get command success rate."""
        if self.commands_processed == 0:
            return 0.0
        successful_commands = len([cmd for cmd in self.commands if cmd.status == VoiceCommandStatus.SUCCESS])
        return (successful_commands / self.commands_processed) * 100
    
    def end_session(self):
        """End the voice session."""
        self.status = VoiceSessionStatus.ENDED
        self.end_time = func.now()
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = func.now()
    
    def increment_command_count(self):
        """Increment processed command count."""
        self.commands_processed += 1
    
    def increment_error_count(self):
        """Increment error count."""
        self.error_count += 1
    
    def update_confidence_avg(self, new_confidence: float):
        """Update average confidence score."""
        if self.confidence_avg == 0.0:
            self.confidence_avg = new_confidence
        else:
            # Calculate running average
            total_confidence = self.confidence_avg * (self.commands_processed - 1) + new_confidence
            self.confidence_avg = total_confidence / self.commands_processed


class VoiceCommand(Base):
    """Voice command model for tracking individual voice commands."""
    
    __tablename__ = "voice_commands"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Command relationships
    session_id = Column(UUID(as_uuid=True), ForeignKey("voice_sessions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Command information
    command_text = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    status = Column(Enum(VoiceCommandStatus), default=VoiceCommandStatus.PROCESSING, nullable=False)
    
    # Processing metrics
    confidence = Column(Float, default=0.0)
    processing_time = Column(Float, default=0.0)  # Processing time in seconds
    response_time = Column(Float, default=0.0)  # Total response time in seconds
    
    # Command data
    entities = Column(JSON, default={})
    response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Voice processing metadata
    audio_url = Column(Text, nullable=True)
    audio_duration = Column(Float, default=0.0)
    language = Column(String(10), default="en-US")
    audio_quality = Column(Float, default=0.0)
    
    # Command metadata
    metadata = Column(JSON, default={
        "ai_model_used": None,
        "fallback_used": False,
        "retry_count": 0,
        "user_feedback": None,
        "context": None
    })
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    session = relationship("VoiceSession", back_populates="commands")
    user = relationship("User")
    
    def __repr__(self):
        return f"<VoiceCommand(id={self.id}, intent='{self.intent}', status='{self.status}')>"
    
    @property
    def is_successful(self) -> bool:
        """Check if command was successful."""
        return self.status == VoiceCommandStatus.SUCCESS
    
    @property
    def is_failed(self) -> bool:
        """Check if command failed."""
        return self.status == VoiceCommandStatus.FAILED
    
    def mark_successful(self, response: str = None, processing_time: float = None):
        """Mark command as successful."""
        self.status = VoiceCommandStatus.SUCCESS
        self.response = response
        self.processing_time = processing_time or 0.0
        self.processed_at = func.now()
    
    def mark_failed(self, error_message: str = None, processing_time: float = None):
        """Mark command as failed."""
        self.status = VoiceCommandStatus.FAILED
        self.error_message = error_message
        self.processing_time = processing_time or 0.0
        self.processed_at = func.now()
    
    def update_entities(self, entities: dict):
        """Update command entities."""
        current_entities = self.entities or {}
        current_entities.update(entities)
        self.entities = current_entities
    
    def add_user_feedback(self, feedback: str):
        """Add user feedback for the command."""
        current_metadata = self.metadata or {}
        current_metadata["user_feedback"] = feedback
        self.metadata = current_metadata


class VoiceAnalytics(Base):
    """Voice analytics model for tracking voice usage patterns and performance."""
    
    __tablename__ = "voice_analytics"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Analytics relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Analytics period
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String(20), default="daily")  # daily, weekly, monthly
    
    # Usage metrics
    total_commands = Column(Integer, default=0)
    successful_commands = Column(Integer, default=0)
    failed_commands = Column(Integer, default=0)
    
    # Performance metrics
    average_confidence = Column(Float, default=0.0)
    average_processing_time = Column(Float, default=0.0)
    average_response_time = Column(Float, default=0.0)
    
    # Command type analytics
    command_types = Column(JSON, default={})  # {"create_task": 10, "mark_complete": 5}
    intent_distribution = Column(JSON, default={})  # {"task_management": 0.6, "project_management": 0.4}
    
    # Error analytics
    error_types = Column(JSON, default={})  # {"low_confidence": 3, "audio_quality": 1}
    error_frequency = Column(JSON, default={})
    
    # User behavior analytics
    session_count = Column(Integer, default=0)
    total_session_duration = Column(Float, default=0.0)
    average_session_duration = Column(Float, default=0.0)
    
    # Voice quality analytics
    average_audio_quality = Column(Float, default=0.0)
    average_background_noise = Column(Float, default=0.0)
    language_distribution = Column(JSON, default={})  # {"en-US": 0.9, "es-ES": 0.1}
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<VoiceAnalytics(id={self.id}, user_id={self.user_id}, date='{self.date}')>"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_commands == 0:
            return 0.0
        return (self.successful_commands / self.total_commands) * 100
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage."""
        if self.total_commands == 0:
            return 0.0
        return (self.failed_commands / self.total_commands) * 100
    
    def update_metrics(self, command_data: dict):
        """Update analytics with new command data."""
        self.total_commands += 1
        
        if command_data.get("success", False):
            self.successful_commands += 1
        else:
            self.failed_commands += 1
        
        # Update averages
        new_confidence = command_data.get("confidence", 0.0)
        new_processing_time = command_data.get("processing_time", 0.0)
        new_response_time = command_data.get("response_time", 0.0)
        
        # Calculate running averages
        if self.average_confidence == 0.0:
            self.average_confidence = new_confidence
        else:
            total_confidence = self.average_confidence * (self.total_commands - 1) + new_confidence
            self.average_confidence = total_confidence / self.total_commands
        
        if self.average_processing_time == 0.0:
            self.average_processing_time = new_processing_time
        else:
            total_processing = self.average_processing_time * (self.total_commands - 1) + new_processing_time
            self.average_processing_time = total_processing / self.total_commands
        
        if self.average_response_time == 0.0:
            self.average_response_time = new_response_time
        else:
            total_response = self.average_response_time * (self.total_commands - 1) + new_response_time
            self.average_response_time = total_response / self.total_commands
        
        # Update command types
        intent = command_data.get("intent", "unknown")
        current_types = self.command_types or {}
        current_types[intent] = current_types.get(intent, 0) + 1
        self.command_types = current_types
