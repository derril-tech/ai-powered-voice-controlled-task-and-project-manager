"""
File upload service for the Voice AI Task Manager.

This service handles file uploads including voice audio files, user avatars,
and other media using Cloudinary cloud storage.
"""

import asyncio
import logging
import os
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import base64
import io

import cloudinary
import cloudinary.uploader
import cloudinary.api

from ..config import settings

logger = logging.getLogger(__name__)


class FileUploadService:
    """Service for handling file uploads and cloud storage."""
    
    def __init__(self):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
        
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_audio_formats = ['.wav', '.mp3', '.m4a', '.webm', '.ogg']
        self.allowed_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    async def upload_voice_audio(self, audio_data: bytes, user_id: str, 
                               session_id: str = None) -> Dict[str, Any]:
        """
        Upload voice audio file to cloud storage.
        
        Args:
            audio_data: Raw audio data in bytes
            user_id: User ID for the audio
            session_id: Voice session ID (optional)
            
        Returns:
            Dictionary with upload result and file URL
        """
        try:
            # Validate audio data
            validation_result = await self._validate_audio_file(audio_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"voice_audio/{user_id}/{file_id}.wav"
            
            # Upload to Cloudinary
            upload_result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                io.BytesIO(audio_data),
                public_id=filename,
                resource_type="video",  # Cloudinary treats audio as video
                format="wav",
                folder="voice_ai_task_manager",
                tags=["voice_audio", f"user_{user_id}"],
                context={
                    "user_id": user_id,
                    "session_id": session_id,
                    "upload_type": "voice_audio",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            logger.info(f"Voice audio uploaded successfully: {upload_result['secure_url']}")
            
            return {
                "success": True,
                "file_url": upload_result["secure_url"],
                "file_id": file_id,
                "filename": filename,
                "size": len(audio_data),
                "format": "wav",
                "upload_time": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Voice audio upload failed: {e}")
            return {
                "success": False,
                "error": f"Upload failed: {str(e)}"
            }
    
    async def upload_user_avatar(self, image_data: bytes, user_id: str, 
                               file_extension: str = ".jpg") -> Dict[str, Any]:
        """
        Upload user avatar image.
        
        Args:
            image_data: Raw image data in bytes
            user_id: User ID
            file_extension: File extension (.jpg, .png, etc.)
            
        Returns:
            Dictionary with upload result and image URL
        """
        try:
            # Validate image data
            validation_result = await self._validate_image_file(image_data, file_extension)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"avatars/{user_id}/{file_id}{file_extension}"
            
            # Upload to Cloudinary with transformations
            upload_result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                io.BytesIO(image_data),
                public_id=filename,
                resource_type="image",
                folder="voice_ai_task_manager",
                tags=["avatar", f"user_{user_id}"],
                transformation=[
                    {"width": 200, "height": 200, "crop": "fill", "gravity": "face"},
                    {"quality": "auto", "fetch_format": "auto"}
                ],
                context={
                    "user_id": user_id,
                    "upload_type": "avatar",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            logger.info(f"User avatar uploaded successfully: {upload_result['secure_url']}")
            
            return {
                "success": True,
                "image_url": upload_result["secure_url"],
                "file_id": file_id,
                "filename": filename,
                "size": len(image_data),
                "format": file_extension[1:],  # Remove the dot
                "upload_time": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"User avatar upload failed: {e}")
            return {
                "success": False,
                "error": f"Upload failed: {str(e)}"
            }
    
    async def upload_project_file(self, file_data: bytes, project_id: str, 
                                filename: str, file_type: str) -> Dict[str, Any]:
        """
        Upload project-related file.
        
        Args:
            file_data: Raw file data in bytes
            project_id: Project ID
            filename: Original filename
            file_type: Type of file (document, image, etc.)
            
        Returns:
            Dictionary with upload result and file URL
        """
        try:
            # Validate file
            validation_result = await self._validate_file(file_data, filename)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(filename)[1]
            cloudinary_filename = f"projects/{project_id}/{file_id}{file_extension}"
            
            # Determine resource type
            resource_type = "auto"
            if file_extension.lower() in self.allowed_image_formats:
                resource_type = "image"
            elif file_extension.lower() in self.allowed_audio_formats:
                resource_type = "video"
            
            # Upload to Cloudinary
            upload_result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                io.BytesIO(file_data),
                public_id=cloudinary_filename,
                resource_type=resource_type,
                folder="voice_ai_task_manager",
                tags=["project_file", f"project_{project_id}", file_type],
                context={
                    "project_id": project_id,
                    "original_filename": filename,
                    "file_type": file_type,
                    "upload_type": "project_file",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            logger.info(f"Project file uploaded successfully: {upload_result['secure_url']}")
            
            return {
                "success": True,
                "file_url": upload_result["secure_url"],
                "file_id": file_id,
                "original_filename": filename,
                "cloudinary_filename": cloudinary_filename,
                "size": len(file_data),
                "format": file_extension[1:],
                "upload_time": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Project file upload failed: {e}")
            return {
                "success": False,
                "error": f"Upload failed: {str(e)}"
            }
    
    async def delete_file(self, file_url: str, file_type: str = "auto") -> bool:
        """
        Delete file from cloud storage.
        
        Args:
            file_url: File URL to delete
            file_type: Type of file (image, video, raw)
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Extract public ID from URL
            public_id = self._extract_public_id_from_url(file_url)
            if not public_id:
                logger.error("Could not extract public ID from URL")
                return False
            
            # Delete from Cloudinary
            result = await asyncio.to_thread(
                cloudinary.uploader.destroy,
                public_id,
                resource_type=file_type
            )
            
            if result.get("result") == "ok":
                logger.info(f"File deleted successfully: {public_id}")
                return True
            else:
                logger.error(f"File deletion failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return False
    
    async def get_file_info(self, file_url: str) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            file_url: File URL
            
        Returns:
            Dictionary with file information
        """
        try:
            # Extract public ID from URL
            public_id = self._extract_public_id_from_url(file_url)
            if not public_id:
                return {"error": "Could not extract public ID from URL"}
            
            # Get file info from Cloudinary
            result = await asyncio.to_thread(
                cloudinary.api.resource,
                public_id
            )
            
            return {
                "success": True,
                "public_id": result.get("public_id"),
                "url": result.get("secure_url"),
                "format": result.get("format"),
                "size": result.get("bytes"),
                "width": result.get("width"),
                "height": result.get("height"),
                "created_at": result.get("created_at"),
                "tags": result.get("tags", []),
                "context": result.get("context", {})
            }
            
        except Exception as e:
            logger.error(f"Get file info failed: {e}")
            return {"error": str(e)}
    
    async def _validate_audio_file(self, audio_data: bytes) -> Dict[str, Any]:
        """Validate audio file data."""
        if not audio_data:
            return {"valid": False, "error": "No audio data provided"}
        
        if len(audio_data) > self.max_file_size:
            return {"valid": False, "error": f"Audio file too large. Max size: {self.max_file_size} bytes"}
        
        if len(audio_data) < 1000:  # Minimum reasonable audio size
            return {"valid": False, "error": "Audio file too small to be valid"}
        
        return {"valid": True}
    
    async def _validate_image_file(self, image_data: bytes, file_extension: str) -> Dict[str, Any]:
        """Validate image file data."""
        if not image_data:
            return {"valid": False, "error": "No image data provided"}
        
        if len(image_data) > self.max_file_size:
            return {"valid": False, "error": f"Image file too large. Max size: {self.max_file_size} bytes"}
        
        if file_extension.lower() not in self.allowed_image_formats:
            return {"valid": False, "error": f"Unsupported image format: {file_extension}"}
        
        return {"valid": True}
    
    async def _validate_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Validate general file data."""
        if not file_data:
            return {"valid": False, "error": "No file data provided"}
        
        if len(file_data) > self.max_file_size:
            return {"valid": False, "error": f"File too large. Max size: {self.max_file_size} bytes"}
        
        file_extension = os.path.splitext(filename)[1].lower()
        allowed_formats = self.allowed_audio_formats + self.allowed_image_formats + ['.pdf', '.doc', '.docx', '.txt']
        
        if file_extension not in allowed_formats:
            return {"valid": False, "error": f"Unsupported file format: {file_extension}"}
        
        return {"valid": True}
    
    def _extract_public_id_from_url(self, file_url: str) -> Optional[str]:
        """Extract public ID from Cloudinary URL."""
        try:
            # Parse Cloudinary URL to extract public ID
            # Example: https://res.cloudinary.com/cloud_name/video/upload/v1234567890/folder/file.jpg
            parts = file_url.split('/')
            
            # Find the upload part and get everything after it
            upload_index = -1
            for i, part in enumerate(parts):
                if part == "upload":
                    upload_index = i
                    break
            
            if upload_index == -1:
                return None
            
            # Get the public ID (everything after upload, excluding version)
            public_id_parts = parts[upload_index + 2:]  # Skip upload and version
            
            # Remove file extension for the public ID
            public_id = '/'.join(public_id_parts)
            if '.' in public_id:
                public_id = os.path.splitext(public_id)[0]
            
            return public_id
            
        except Exception as e:
            logger.error(f"Failed to extract public ID from URL: {e}")
            return None
    
    async def cleanup_old_files(self, days_old: int = 30) -> Dict[str, Any]:
        """
        Clean up old files from cloud storage.
        
        Args:
            days_old: Number of days old to consider for cleanup
            
        Returns:
            Dictionary with cleanup results
        """
        try:
            # Get list of old files
            old_files = await asyncio.to_thread(
                cloudinary.api.resources,
                type="upload",
                max_results=100,
                tags=["voice_ai_task_manager"]
            )
            
            deleted_count = 0
            failed_count = 0
            
            for resource in old_files.get("resources", []):
                created_at = resource.get("created_at")
                if created_at:
                    # Check if file is older than specified days
                    file_date = datetime.fromtimestamp(created_at, tz=timezone.utc)
                    days_diff = (datetime.now(timezone.utc) - file_date).days
                    
                    if days_diff > days_old:
                        # Delete the file
                        try:
                            result = await asyncio.to_thread(
                                cloudinary.uploader.destroy,
                                resource["public_id"],
                                resource_type=resource.get("resource_type", "image")
                            )
                            
                            if result.get("result") == "ok":
                                deleted_count += 1
                                logger.info(f"Deleted old file: {resource['public_id']}")
                            else:
                                failed_count += 1
                                logger.error(f"Failed to delete file: {resource['public_id']}")
                                
                        except Exception as e:
                            failed_count += 1
                            logger.error(f"Error deleting file {resource['public_id']}: {e}")
            
            logger.info(f"Cleanup completed: {deleted_count} files deleted, {failed_count} failed")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "failed_count": failed_count,
                "total_processed": len(old_files.get("resources", []))
            }
            
        except Exception as e:
            logger.error(f"File cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
