"""
AI Integration Service for the Voice AI Task Manager.

This service handles all AI-related operations including:
- OpenAI GPT-4 for general voice understanding
- Claude API for complex reasoning tasks
- LangChain for orchestration and context management
- Speech-to-text conversion with Whisper
- Intent recognition and entity extraction
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional, List
import base64
import io

import httpx
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

from ..config import settings

logger = logging.getLogger(__name__)


class AIIntegrationService:
    """Service for integrating with various AI providers."""
    
    def __init__(self):
        # Initialize OpenAI client
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize Claude client
        self.claude_client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)
        
        # Initialize LangChain models
        self.openai_llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.1,
            max_tokens=1000
        )
        
        self.claude_llm = ChatAnthropic(
            model=settings.CLAUDE_MODEL,
            temperature=0.1,
            max_tokens=1000
        )
        
        # Voice command patterns for intent recognition
        self.voice_patterns = {
            "create_task": [
                "create.*task.*called\\s+(.+)",
                "add.*task\\s+(.+)",
                "new.*task\\s+(.+)",
                "create.*task\\s+(.+)",
                "add.*task.*called\\s+(.+)"
            ],
            "complete_task": [
                "mark\\s+(.+)\\s+as\\s+complete",
                "complete\\s+(.+)",
                "finish\\s+(.+)",
                "mark\\s+(.+)\\s+done",
                "task\\s+(.+)\\s+complete"
            ],
            "create_project": [
                "create.*project.*called\\s+(.+)",
                "new.*project\\s+(.+)",
                "start.*project\\s+(.+)",
                "create.*project\\s+(.+)"
            ],
            "list_tasks": [
                "show.*my.*tasks",
                "list.*my.*tasks",
                "what.*are.*my.*tasks",
                "display.*tasks",
                "get.*my.*tasks"
            ],
            "list_projects": [
                "show.*my.*projects",
                "list.*my.*projects",
                "what.*are.*my.*projects",
                "display.*projects",
                "get.*my.*projects"
            ],
            "get_status": [
                "status.*of\\s+(.+)",
                "how.*is\\s+(.+)",
                "what.*status.*of\\s+(.+)",
                "check.*status.*of\\s+(.+)"
            ],
            "help": [
                "help",
                "what.*can.*i.*do",
                "show.*commands",
                "available.*commands",
                "voice.*commands"
            ]
        }
    
    async def speech_to_text(self, audio_data: bytes, language: str = "en-US") -> Dict[str, Any]:
        """
        Convert speech to text using OpenAI Whisper.
        
        Args:
            audio_data: Raw audio data in bytes
            language: Language code for processing
            
        Returns:
            Dictionary with transcription and confidence
        """
        try:
            # Create a file-like object from audio data
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"  # Whisper expects a filename
            
            # Use OpenAI Whisper for speech-to-text
            response = await self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json"
            )
            
            # Extract transcription and confidence
            transcription = response.text
            confidence = getattr(response, 'confidence', 0.9)  # Default confidence if not provided
            
            logger.info(f"Speech-to-text successful: {transcription[:50]}...")
            
            return {
                "success": True,
                "transcription": transcription,
                "confidence": confidence,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Speech-to-text failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": "",
                "confidence": 0.0
            }
    
    async def recognize_intent(self, transcription: str, user_id: str) -> Dict[str, Any]:
        """
        Recognize intent and extract entities from transcription.
        
        Args:
            transcription: Text transcription of voice input
            user_id: User ID for context
            
        Returns:
            Dictionary with intent and entities
        """
        try:
            # First, try pattern matching for common intents
            pattern_result = self._pattern_match_intent(transcription)
            if pattern_result["confidence"] > 0.8:
                return pattern_result
            
            # If pattern matching is not confident, use AI
            return await self._ai_intent_recognition(transcription, user_id)
            
        except Exception as e:
            logger.error(f"Intent recognition failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "intent": "unknown",
                "entities": {},
                "confidence": 0.0
            }
    
    def _pattern_match_intent(self, transcription: str) -> Dict[str, Any]:
        """Use pattern matching for intent recognition."""
        import re
        
        transcription_lower = transcription.lower()
        best_match = {"intent": "unknown", "confidence": 0.0, "entities": {}}
        
        for intent, patterns in self.voice_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, transcription_lower)
                if match:
                    confidence = 0.9  # High confidence for pattern matches
                    entities = self._extract_entities_from_match(intent, match, transcription)
                    
                    if confidence > best_match["confidence"]:
                        best_match = {
                            "intent": intent,
                            "confidence": confidence,
                            "entities": entities
                        }
        
        return {
            "success": True,
            "intent": best_match["intent"],
            "entities": best_match["entities"],
            "confidence": best_match["confidence"]
        }
    
    def _extract_entities_from_match(self, intent: str, match, transcription: str) -> Dict[str, Any]:
        """Extract entities from pattern match."""
        entities = {}
        
        if intent == "create_task":
            if match.groups():
                entities["task_name"] = match.group(1).strip()
        elif intent == "complete_task":
            if match.groups():
                entities["task_name"] = match.group(1).strip()
        elif intent == "create_project":
            if match.groups():
                entities["project_name"] = match.group(1).strip()
        elif intent == "get_status":
            if match.groups():
                entities["item_name"] = match.group(1).strip()
        
        return entities
    
    async def _ai_intent_recognition(self, transcription: str, user_id: str) -> Dict[str, Any]:
        """Use AI for intent recognition when pattern matching fails."""
        try:
            # Create prompt for intent recognition
            prompt = f"""
            Analyze the following voice command and identify the intent and extract relevant entities.
            
            Voice command: "{transcription}"
            
            Possible intents:
            - create_task: User wants to create a new task
            - complete_task: User wants to mark a task as complete
            - create_project: User wants to create a new project
            - list_tasks: User wants to see their tasks
            - list_projects: User wants to see their projects
            - get_status: User wants to check status of something
            - assign_task: User wants to assign a task to someone
            - help: User wants help or to see available commands
            
            Respond with a JSON object containing:
            {{
                "intent": "the_identified_intent",
                "confidence": 0.0-1.0,
                "entities": {{
                    "task_name": "extracted task name if any",
                    "project_name": "extracted project name if any",
                    "assignee": "extracted assignee if any",
                    "status": "extracted status if any",
                    "priority": "extracted priority if any",
                    "due_date": "extracted due date if any"
                }}
            }}
            """
            
            # Use Claude for intent recognition (better at structured output)
            response = await self.claude_client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=500,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse the response
            content = response.content[0].text
            try:
                result = json.loads(content)
                return {
                    "success": True,
                    "intent": result.get("intent", "unknown"),
                    "entities": result.get("entities", {}),
                    "confidence": result.get("confidence", 0.5)
                }
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI intent recognition response")
                return {
                    "success": False,
                    "intent": "unknown",
                    "entities": {},
                    "confidence": 0.0
                }
                
        except Exception as e:
            logger.error(f"AI intent recognition failed: {e}")
            return {
                "success": False,
                "intent": "unknown",
                "entities": {},
                "confidence": 0.0
            }
    
    async def generate_response(self, transcription: str, intent: str, 
                              action_result: Dict[str, Any], response_type: str) -> str:
        """
        Generate natural language response for voice commands.
        
        Args:
            transcription: Original voice transcription
            intent: Recognized intent
            action_result: Result of action execution
            response_type: Type of response (success/error)
            
        Returns:
            Natural language response string
        """
        try:
            if response_type == "success":
                return await self._generate_success_response(transcription, intent, action_result)
            else:
                return await self._generate_error_response(transcription, intent, action_result)
                
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return "I'm sorry, I encountered an error processing your request."
    
    async def _generate_success_response(self, transcription: str, intent: str, 
                                       action_result: Dict[str, Any]) -> str:
        """Generate success response."""
        try:
            # Use Claude for natural response generation
            prompt = f"""
            Generate a natural, conversational response for a successful voice command.
            
            Original command: "{transcription}"
            Intent: {intent}
            Action result: {action_result.get('message', 'Action completed successfully')}
            
            The response should be:
            - Natural and conversational
            - Confirm what was done
            - Be concise but informative
            - Sound like a helpful assistant
            
            Response:
            """
            
            response = await self.claude_client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=200,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Success response generation failed: {e}")
            return action_result.get('message', 'Action completed successfully.')
    
    async def _generate_error_response(self, transcription: str, intent: str, 
                                     action_result: Dict[str, Any]) -> str:
        """Generate error response."""
        try:
            # Use Claude for natural error response
            prompt = f"""
            Generate a helpful error response for a failed voice command.
            
            Original command: "{transcription}"
            Intent: {intent}
            Error: {action_result.get('message', 'An error occurred')}
            
            The response should be:
            - Apologetic but not overly so
            - Explain what went wrong
            - Suggest how to fix it
            - Be encouraging to try again
            
            Response:
            """
            
            response = await self.claude_client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=200,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Error response generation failed: {e}")
            return f"I'm sorry, I couldn't complete that action. {action_result.get('message', 'Please try again.')}"
    
    async def analyze_voice_context(self, transcription: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze voice input with user context for better understanding.
        
        Args:
            transcription: Voice transcription
            user_context: User context and preferences
            
        Returns:
            Analysis results with context insights
        """
        try:
            prompt = f"""
            Analyze this voice command with user context to provide better understanding.
            
            Voice command: "{transcription}"
            User context: {json.dumps(user_context, indent=2)}
            
            Provide analysis including:
            - Likely intent
            - Extracted entities
            - Context relevance
            - Confidence level
            - Suggestions for improvement
            
            Respond in JSON format.
            """
            
            response = await self.claude_client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=500,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"error": "Failed to parse analysis response"}
                
        except Exception as e:
            logger.error(f"Voice context analysis failed: {e}")
            return {"error": str(e)}
    
    async def get_voice_suggestions(self, partial_transcription: str, user_id: str) -> List[str]:
        """
        Get voice command suggestions based on partial input.
        
        Args:
            partial_transcription: Partial voice transcription
            user_id: User ID for context
            
        Returns:
            List of suggested voice commands
        """
        try:
            prompt = f"""
            Based on this partial voice input, suggest possible complete voice commands.
            
            Partial input: "{partial_transcription}"
            
            Provide 3-5 suggestions for what the user might be trying to say.
            Focus on task and project management commands.
            
            Respond with a JSON array of suggestions.
            """
            
            response = await self.claude_client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=300,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text
            try:
                suggestions = json.loads(content)
                return suggestions if isinstance(suggestions, list) else []
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            logger.error(f"Voice suggestions failed: {e}")
            return []
    
    async def validate_voice_command(self, transcription: str, intent: str, 
                                   entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate voice command for completeness and correctness.
        
        Args:
            transcription: Voice transcription
            intent: Recognized intent
            entities: Extracted entities
            
        Returns:
            Validation result with suggestions
        """
        try:
            prompt = f"""
            Validate this voice command for completeness and correctness.
            
            Transcription: "{transcription}"
            Intent: {intent}
            Entities: {json.dumps(entities, indent=2)}
            
            Check for:
            - Missing required information
            - Ambiguous references
            - Incorrect entity types
            - Suggest improvements
            
            Respond with validation results in JSON format.
            """
            
            response = await self.claude_client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=400,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"valid": True, "suggestions": []}
                
        except Exception as e:
            logger.error(f"Voice command validation failed: {e}")
            return {"valid": True, "suggestions": []}
