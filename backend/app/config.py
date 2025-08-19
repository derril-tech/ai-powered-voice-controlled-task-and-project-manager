"""
Configuration settings for the Voice AI Task Manager backend.

This module contains all configuration settings including database connections,
AI API keys, security settings, and voice processing parameters.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    APP_NAME: str = "Voice AI Task Manager API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database settings
    DATABASE_URL: str = Field(env="DATABASE_URL")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Redis settings
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # JWT settings
    JWT_SECRET_KEY: str = Field(env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # AI API settings
    OPENAI_API_KEY: str = Field(env="OPENAI_API_KEY")
    CLAUDE_API_KEY: str = Field(env="CLAUDE_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    CLAUDE_MODEL: str = Field(default="claude-3-sonnet-20240229", env="CLAUDE_MODEL")
    
    # Voice processing settings
    VOICE_PROCESSING_TIMEOUT: int = Field(default=30, env="VOICE_PROCESSING_TIMEOUT")
    MAX_AUDIO_SIZE: int = Field(default=10485760, env="MAX_AUDIO_SIZE")  # 10MB
    VOICE_CONFIDENCE_THRESHOLD: float = Field(default=0.7, env="VOICE_CONFIDENCE_THRESHOLD")
    VOICE_LANGUAGE: str = Field(default="en-US", env="VOICE_LANGUAGE")
    
    # File upload settings
    CLOUDINARY_CLOUD_NAME: str = Field(env="CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = Field(env="CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = Field(env="CLOUDINARY_API_SECRET")
    MAX_FILE_SIZE: int = Field(default=52428800, env="MAX_FILE_SIZE")  # 50MB
    
    # Email settings
    SENDGRID_API_KEY: str = Field(env="SENDGRID_API_KEY")
    FROM_EMAIL: str = Field(env="FROM_EMAIL")
    
    # Security settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "https://voice-task-manager.com"],
        env="CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1", "voice-task-manager.com"],
        env="ALLOWED_HOSTS"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Voice session settings
    VOICE_SESSION_TIMEOUT: int = Field(default=3600, env="VOICE_SESSION_TIMEOUT")  # 1 hour
    MAX_CONCURRENT_VOICE_SESSIONS: int = Field(default=10, env="MAX_CONCURRENT_VOICE_SESSIONS")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Monitoring settings
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    # Voice analytics settings
    VOICE_ANALYTICS_ENABLED: bool = Field(default=True, env="VOICE_ANALYTICS_ENABLED")
    VOICE_DATA_RETENTION_DAYS: int = Field(default=30, env="VOICE_DATA_RETENTION_DAYS")
    
    # LangChain settings
    LANGCHAIN_TRACING_V2: bool = Field(default=False, env="LANGCHAIN_TRACING_V2")
    LANGCHAIN_ENDPOINT: Optional[str] = Field(default=None, env="LANGCHAIN_ENDPOINT")
    LANGCHAIN_API_KEY: Optional[str] = Field(default=None, env="LANGCHAIN_API_KEY")
    
    # pgvector settings
    VECTOR_DIMENSION: int = Field(default=1536, env="VECTOR_DIMENSION")  # OpenAI embedding dimension
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Validate required settings
def validate_settings():
    """Validate that all required settings are properly configured."""
    required_settings = [
        "DATABASE_URL",
        "JWT_SECRET_KEY", 
        "OPENAI_API_KEY",
        "CLAUDE_API_KEY",
        "CLOUDINARY_CLOUD_NAME",
        "CLOUDINARY_API_KEY",
        "CLOUDINARY_API_SECRET",
        "SENDGRID_API_KEY",
        "FROM_EMAIL"
    ]
    
    missing_settings = []
    for setting in required_settings:
        if not getattr(settings, setting, None):
            missing_settings.append(setting)
    
    if missing_settings:
        raise ValueError(f"Missing required settings: {', '.join(missing_settings)}")


# Validate settings on import
try:
    validate_settings()
except ValueError as e:
    print(f"Configuration Error: {e}")
    raise
