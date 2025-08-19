"""
Database configuration and connection setup for the Voice AI Task Manager.

This module handles database connections, session management, and provides
async database support with SQLAlchemy 2.0 and PostgreSQL with pgvector extension.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
from sqlalchemy import MetaData
import logging

from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    # Enable pgvector extension
    connect_args={
        "server_settings": {
            "application_name": "voice_ai_task_manager"
        }
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Create declarative base
Base = declarative_base()

# Metadata for database operations
metadata = MetaData()


async def init_db():
    """Initialize database with all tables and extensions."""
    try:
        async with engine.begin() as conn:
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def close_db():
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")


# Database health check
async def check_db_health() -> bool:
    """Check database connection health."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


# Voice-specific database utilities
async def get_voice_session_stats(session: AsyncSession, user_id: str):
    """Get voice session statistics for a user."""
    from .models.voice import VoiceSession
    
    try:
        # Get total sessions
        total_sessions = await session.execute(
            "SELECT COUNT(*) FROM voice_sessions WHERE user_id = :user_id",
            {"user_id": user_id}
        )
        
        # Get average confidence
        avg_confidence = await session.execute(
            "SELECT AVG(confidence_avg) FROM voice_sessions WHERE user_id = :user_id",
            {"user_id": user_id}
        )
        
        # Get total commands processed
        total_commands = await session.execute(
            "SELECT SUM(commands_processed) FROM voice_sessions WHERE user_id = :user_id",
            {"user_id": user_id}
        )
        
        return {
            "total_sessions": total_sessions.scalar() or 0,
            "average_confidence": float(avg_confidence.scalar() or 0),
            "total_commands": total_commands.scalar() or 0
        }
    except Exception as e:
        logger.error(f"Error getting voice session stats: {e}")
        return {
            "total_sessions": 0,
            "average_confidence": 0.0,
            "total_commands": 0
        }


async def cleanup_old_voice_data(session: AsyncSession, days: int = 30):
    """Clean up old voice data based on retention policy."""
    try:
        # Delete old voice sessions
        result = await session.execute(
            """
            DELETE FROM voice_sessions 
            WHERE created_at < NOW() - INTERVAL ':days days'
            """,
            {"days": days}
        )
        
        # Delete old voice commands
        result2 = await session.execute(
            """
            DELETE FROM voice_commands 
            WHERE created_at < NOW() - INTERVAL ':days days'
            """,
            {"days": days}
        )
        
        await session.commit()
        
        logger.info(f"Cleaned up {result.rowcount} old voice sessions and {result2.rowcount} voice commands")
        return result.rowcount + result2.rowcount
    except Exception as e:
        await session.rollback()
        logger.error(f"Error cleaning up old voice data: {e}")
        raise
