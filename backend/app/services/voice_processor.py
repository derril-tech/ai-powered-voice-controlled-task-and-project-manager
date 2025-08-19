"""
Voice processing service for the Voice AI Task Manager.

This service handles the complete voice processing pipeline including:
- Audio preprocessing and validation
- Speech-to-text conversion
- Intent recognition and entity extraction
- Action execution and response generation
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import base64
import io

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..config import settings
from ..models.voice import VoiceSession, VoiceCommand, VoiceSessionStatus, VoiceCommandStatus
from ..models.user import User
from .ai_integration import AIIntegrationService
from .notification import NotificationService

logger = logging.getLogger(__name__)


class VoiceProcessingResult:
    """Result of voice processing operation."""
    
    def __init__(self, success: bool, transcription: str = None, intent: str = None,
                 confidence: float = 0.0, entities: Dict[str, Any] = None,
                 response: str = None, error_message: str = None,
                 processing_time: float = 0.0, voice_metadata: Dict[str, Any] = None):
        self.success = success
        self.transcription = transcription
        self.intent = intent
        self.confidence = confidence
        self.entities = entities or {}
        self.response = response
        self.error_message = error_message
        self.processing_time = processing_time
        self.voice_metadata = voice_metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "transcription": self.transcription,
            "intent": self.intent,
            "confidence": self.confidence,
            "entities": self.entities,
            "response": self.response,
            "error_message": self.error_message,
            "processing_time": self.processing_time,
            "voice_metadata": self.voice_metadata
        }


class VoiceProcessor:
    """Core voice processing service."""
    
    def __init__(self):
        self.ai_service = AIIntegrationService()
        self.notification_service = NotificationService()
        self.processing_timeout = settings.VOICE_PROCESSING_TIMEOUT
        self.max_audio_size = settings.MAX_AUDIO_SIZE
        self.confidence_threshold = settings.VOICE_CONFIDENCE_THRESHOLD
    
    async def process_voice_command(self, audio_data: bytes, user_id: str, 
                                  session_id: str = None, language: str = "en-US") -> VoiceProcessingResult:
        """
        Process voice command through the complete pipeline.
        
        Args:
            audio_data: Raw audio data in bytes
            user_id: User ID for the command
            session_id: Voice session ID (optional)
            language: Language code for processing
            
        Returns:
            VoiceProcessingResult with processing results
        """
        start_time = time.time()
        
        try:
            # Step 1: Validate audio data
            validation_result = await self._validate_audio_data(audio_data)
            if not validation_result["valid"]:
                return VoiceProcessingResult(
                    success=False,
                    error_message=validation_result["error"],
                    processing_time=time.time() - start_time
                )
            
            # Step 2: Preprocess audio
            processed_audio = await self._preprocess_audio(audio_data)
            
            # Step 3: Speech-to-text conversion
            transcription_result = await self._speech_to_text(processed_audio, language)
            if not transcription_result["success"]:
                return VoiceProcessingResult(
                    success=False,
                    error_message="Failed to convert speech to text",
                    processing_time=time.time() - start_time
                )
            
            transcription = transcription_result["transcription"]
            confidence = transcription_result["confidence"]
            
            # Step 4: Intent recognition and entity extraction
            intent_result = await self._recognize_intent(transcription, user_id)
            if not intent_result["success"]:
                return VoiceProcessingResult(
                    success=False,
                    transcription=transcription,
                    error_message="Failed to recognize intent",
                    processing_time=time.time() - start_time
                )
            
            intent = intent_result["intent"]
            entities = intent_result["entities"]
            
            # Step 5: Execute action based on intent
            action_result = await self._execute_action(intent, entities, user_id)
            
            # Step 6: Generate response
            response = await self._generate_response(action_result, transcription, intent)
            
            # Step 7: Save voice command to database
            await self._save_voice_command(
                session_id, user_id, transcription, intent, confidence,
                entities, response, time.time() - start_time
            )
            
            # Step 8: Send notification if needed
            await self._send_voice_notification(user_id, intent, action_result)
            
            processing_time = time.time() - start_time
            
            return VoiceProcessingResult(
                success=True,
                transcription=transcription,
                intent=intent,
                confidence=confidence,
                entities=entities,
                response=response,
                processing_time=processing_time,
                voice_metadata={
                    "language": language,
                    "audio_size": len(audio_data),
                    "session_id": session_id
                }
            )
            
        except Exception as e:
            logger.error(f"Voice processing failed: {e}", exc_info=True)
            return VoiceProcessingResult(
                success=False,
                error_message=f"Voice processing failed: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    async def _validate_audio_data(self, audio_data: bytes) -> Dict[str, Any]:
        """Validate audio data format and size."""
        if not audio_data:
            return {"valid": False, "error": "No audio data provided"}
        
        if len(audio_data) > self.max_audio_size:
            return {"valid": False, "error": f"Audio file too large. Max size: {self.max_audio_size} bytes"}
        
        # Check if it's valid audio data (basic check)
        if len(audio_data) < 100:  # Minimum reasonable audio size
            return {"valid": False, "error": "Audio data too small to be valid"}
        
        return {"valid": True}
    
    async def _preprocess_audio(self, audio_data: bytes) -> bytes:
        """Preprocess audio data for better recognition."""
        # Basic preprocessing - in production, you might want to:
        # - Convert to proper format (WAV, MP3)
        # - Normalize audio levels
        # - Remove background noise
        # - Resample to optimal frequency
        
        # For now, return as-is
        return audio_data
    
    async def _speech_to_text(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """Convert speech to text using AI services."""
        try:
            # Try OpenAI Whisper first
            result = await self.ai_service.speech_to_text(audio_data, language)
            
            if result["success"]:
                return result
            
            # Fallback to other services if needed
            logger.warning("OpenAI Whisper failed, trying fallback")
            
            # You could implement fallback to other STT services here
            # For now, return the OpenAI result even if it failed
            
            return result
            
        except Exception as e:
            logger.error(f"Speech-to-text conversion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": "",
                "confidence": 0.0
            }
    
    async def _recognize_intent(self, transcription: str, user_id: str) -> Dict[str, Any]:
        """Recognize intent and extract entities from transcription."""
        try:
            result = await self.ai_service.recognize_intent(transcription, user_id)
            return result
        except Exception as e:
            logger.error(f"Intent recognition failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "intent": "unknown",
                "entities": {}
            }
    
    async def _execute_action(self, intent: str, entities: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute action based on recognized intent."""
        try:
            # Map intents to actions
            action_mapping = {
                "create_task": self._create_task,
                "update_task": self._update_task,
                "complete_task": self._complete_task,
                "create_project": self._create_project,
                "update_project": self._update_project,
                "assign_task": self._assign_task,
                "list_tasks": self._list_tasks,
                "list_projects": self._list_projects,
                "get_status": self._get_status,
                "help": self._show_help
            }
            
            action_func = action_mapping.get(intent)
            if action_func:
                return await action_func(entities, user_id)
            else:
                return {
                    "success": False,
                    "message": f"Unknown intent: {intent}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {
                "success": False,
                "message": f"Action execution failed: {str(e)}",
                "data": None
            }
    
    async def _generate_response(self, action_result: Dict[str, Any], 
                               transcription: str, intent: str) -> str:
        """Generate natural language response."""
        try:
            if action_result["success"]:
                # Generate success response
                response = await self.ai_service.generate_response(
                    transcription, intent, action_result, "success"
                )
            else:
                # Generate error response
                response = await self.ai_service.generate_response(
                    transcription, intent, action_result, "error"
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return "I'm sorry, I encountered an error processing your request."
    
    async def _save_voice_command(self, session_id: str, user_id: str, transcription: str,
                                intent: str, confidence: float, entities: Dict[str, Any],
                                response: str, processing_time: float):
        """Save voice command to database."""
        try:
            # This would typically be done in a database session
            # For now, just log the command
            logger.info(f"Voice command saved: {intent} - {transcription}")
            
        except Exception as e:
            logger.error(f"Failed to save voice command: {e}")
    
    async def _send_voice_notification(self, user_id: str, intent: str, action_result: Dict[str, Any]):
        """Send notification for voice command if needed."""
        try:
            if action_result.get("success") and intent in ["create_task", "complete_task", "create_project"]:
                await self.notification_service.send_voice_notification(
                    user_id, intent, action_result
                )
        except Exception as e:
            logger.error(f"Failed to send voice notification: {e}")
    
    # Action implementations
    async def _create_task(self, entities: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create a new task."""
        try:
            task_name = entities.get("task_name")
            if not task_name:
                return {"success": False, "message": "Task name not provided"}
            
            # Here you would create the task in the database
            # For now, return a mock result
            return {
                "success": True,
                "message": f"Task '{task_name}' created successfully",
                "data": {"task_name": task_name, "task_id": "mock_id"}
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to create task: {str(e)}"}
    
    async def _update_task(self, entities: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update an existing task."""
        try:
            task_name = entities.get("task_name")
            status = entities.get("status")
            
            if not task_name:
                return {"success": False, "message": "Task name not provided"}
            
            return {
                "success": True,
                "message": f"Task '{task_name}' updated to {status}",
                "data": {"task_name": task_name, "status": status}
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to update task: {str(e)}"}
    
    async def _complete_task(self, entities: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Mark a task as complete."""
        try:
            task_name = entities.get("task_name")
            
            if not task_name:
                return {"success": False, "message": "Task name not provided"}
            
            return {
                "success": True,
                "message": f"Task '{task_name}' marked as complete",
                "data": {"task_name": task_name, "status": "completed"}
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to complete task: {str(e)}"}
    
    async def _create_project(self, entities: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create a new project."""
        try:
            project_name = entities.get("project_name")
            
            if not project_name:
                return {"success": False, "message": "Project name not provided"}
            
            return {
                "success": True,
                "message": f"Project '{project_name}' created successfully",
                "data": {"project_name": project_name, "project_id": "mock_id"}
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to create project: {str(e)}"}
    
    async def _update_project(self, entities: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update an existing project."""
        try:
            project_name = entities.get("project_name")
            status = entities.get("status")
            
            if not project_name:
                return {"success": False, "message": "Project name not provided"}
            
            return {
                "success": True,
                "message": f"Project '{project_name}' updated to {status}",
                "data": {"project_name": project_name, "status": status}
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to update project: {str(e)}"}
    
    async def _assign_task(self, entities: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Assign a task to a user."""
        try:
            task_name = entities.get("task_name")
            assignee = entities.get("assignee")
            
            if not task_name or not assignee:
                return {"success": False, "message": "Task name and assignee required"}
            
            return {
                "success": True,
                "message": f"Task '{task_name}' assigned to {assignee}",
                "data": {"task_name": task_name, "assignee": assignee}
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to assign task: {str(e)}"}
    
    async def _list_tasks(self, entities: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """List user's tasks."""
        try:
            # Mock task list
            tasks = [
                {"title": "Buy groceries", "status": "pending"},
                {"title": "Review proposal", "status": "completed"}
            ]
            
            return {
                "success": True,
                "message": f"You have {len(tasks)} tasks",
                "data": {"tasks": tasks}
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to list tasks: {str(e)}"}
    
    async def _list_projects(self, entities: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """List user's projects."""
        try:
            # Mock project list
            projects = [
                {"name": "Q4 Planning", "status": "active"},
                {"name": "Website Redesign", "status": "completed"}
            ]
            
            return {
                "success": True,
                "message": f"You have {len(projects)} projects",
                "data": {"projects": projects}
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to list projects: {str(e)}"}
    
    async def _get_status(self, entities: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Get status of tasks or projects."""
        try:
            item_name = entities.get("item_name")
            
            if not item_name:
                return {"success": False, "message": "Item name not provided"}
            
            # Mock status
            status = "in progress"
            
            return {
                "success": True,
                "message": f"{item_name} is {status}",
                "data": {"item_name": item_name, "status": status}
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to get status: {str(e)}"}
    
    async def _show_help(self, entities: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Show available voice commands."""
        try:
            commands = [
                "Create a new task",
                "Mark task as complete", 
                "Create a new project",
                "Show my tasks",
                "Show my projects"
            ]
            
            return {
                "success": True,
                "message": "Here are some voice commands you can try:",
                "data": {"commands": commands}
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to show help: {str(e)}"}
