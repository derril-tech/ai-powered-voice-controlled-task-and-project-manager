"""
Notification service for the Voice AI Task Manager.

This service handles email notifications, real-time alerts, and user communication
for the voice-controlled task management system.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent

from ..config import settings
from ..models.notification import Notification, NotificationType, NotificationPriority

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for handling notifications and alerts."""
    
    def __init__(self):
        self.sendgrid_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        self.from_email = settings.FROM_EMAIL
    
    async def send_voice_notification(self, user_id: str, intent: str, action_result: Dict[str, Any]):
        """
        Send notification for voice command processing.
        
        Args:
            user_id: User ID
            intent: Voice command intent
            action_result: Result of action execution
        """
        try:
            if action_result.get("success"):
                notification_type = NotificationType.VOICE_COMMAND_PROCESSED
                title = "Voice Command Processed"
                message = f"Your voice command '{intent}' was processed successfully."
                priority = NotificationPriority.MEDIUM
            else:
                notification_type = NotificationType.VOICE_COMMAND_FAILED
                title = "Voice Command Failed"
                message = f"Your voice command '{intent}' could not be processed."
                priority = NotificationPriority.HIGH
            
            # Create notification in database
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                priority=priority,
                title=title,
                message=message,
                data={
                    "intent": intent,
                    "action_result": action_result
                }
            )
            
            # Save to database (this would be done in a database session)
            logger.info(f"Voice notification created for user {user_id}: {title}")
            
        except Exception as e:
            logger.error(f"Failed to send voice notification: {e}")
    
    async def send_task_notification(self, user_id: str, task_id: str, notification_type: NotificationType,
                                   title: str, message: str, priority: NotificationPriority = NotificationPriority.MEDIUM):
        """
        Send task-related notification.
        
        Args:
            user_id: User ID
            task_id: Task ID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Notification priority
        """
        try:
            notification = Notification.create_task_notification(
                user_id=user_id,
                task_id=task_id,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority
            )
            
            # Save to database
            logger.info(f"Task notification created for user {user_id}: {title}")
            
        except Exception as e:
            logger.error(f"Failed to send task notification: {e}")
    
    async def send_project_notification(self, user_id: str, project_id: str, notification_type: NotificationType,
                                      title: str, message: str, priority: NotificationPriority = NotificationPriority.MEDIUM):
        """
        Send project-related notification.
        
        Args:
            user_id: User ID
            project_id: Project ID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Notification priority
        """
        try:
            notification = Notification.create_project_notification(
                user_id=user_id,
                project_id=project_id,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority
            )
            
            # Save to database
            logger.info(f"Project notification created for user {user_id}: {title}")
            
        except Exception as e:
            logger.error(f"Failed to send project notification: {e}")
    
    async def send_email_notification(self, to_email: str, subject: str, html_content: str, 
                                    text_content: str = None) -> bool:
        """
        Send email notification using SendGrid.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            from_email = Email(self.from_email)
            to_email_obj = To(to_email)
            
            if text_content:
                content = Content("text/plain", text_content)
                mail = Mail(from_email, to_email_obj, subject, content)
                mail.add_content(HtmlContent(html_content))
            else:
                content = HtmlContent(html_content)
                mail = Mail(from_email, to_email_obj, subject, content)
            
            response = await asyncio.to_thread(
                self.sendgrid_client.send,
                mail
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email to {to_email}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    async def send_task_reminder_email(self, user_email: str, user_name: str, task_title: str, 
                                     due_date: datetime, task_id: str):
        """
        Send task reminder email.
        
        Args:
            user_email: User's email address
            user_name: User's name
            task_title: Task title
            due_date: Task due date
            task_id: Task ID
        """
        try:
            subject = f"Task Reminder: {task_title}"
            
            html_content = f"""
            <html>
            <body>
                <h2>Task Reminder</h2>
                <p>Hello {user_name},</p>
                <p>This is a reminder that your task "<strong>{task_title}</strong>" is due on {due_date.strftime('%B %d, %Y')}.</p>
                <p>Please log in to your dashboard to view and update the task.</p>
                <p>Best regards,<br>Voice AI Task Manager</p>
            </body>
            </html>
            """
            
            text_content = f"""
            Task Reminder
            
            Hello {user_name},
            
            This is a reminder that your task "{task_title}" is due on {due_date.strftime('%B %d, %Y')}.
            
            Please log in to your dashboard to view and update the task.
            
            Best regards,
            Voice AI Task Manager
            """
            
            success = await self.send_email_notification(user_email, subject, html_content, text_content)
            
            if success:
                logger.info(f"Task reminder email sent to {user_email}")
            else:
                logger.error(f"Failed to send task reminder email to {user_email}")
                
        except Exception as e:
            logger.error(f"Task reminder email failed: {e}")
    
    async def send_project_update_email(self, user_email: str, user_name: str, project_name: str,
                                      update_type: str, project_id: str):
        """
        Send project update email.
        
        Args:
            user_email: User's email address
            user_name: User's name
            project_name: Project name
            update_type: Type of update
            project_id: Project ID
        """
        try:
            subject = f"Project Update: {project_name}"
            
            html_content = f"""
            <html>
            <body>
                <h2>Project Update</h2>
                <p>Hello {user_name},</p>
                <p>There has been an update to your project "<strong>{project_name}</strong>".</p>
                <p>Update type: {update_type}</p>
                <p>Please log in to your dashboard to view the latest updates.</p>
                <p>Best regards,<br>Voice AI Task Manager</p>
            </body>
            </html>
            """
            
            text_content = f"""
            Project Update
            
            Hello {user_name},
            
            There has been an update to your project "{project_name}".
            
            Update type: {update_type}
            
            Please log in to your dashboard to view the latest updates.
            
            Best regards,
            Voice AI Task Manager
            """
            
            success = await self.send_email_notification(user_email, subject, html_content, text_content)
            
            if success:
                logger.info(f"Project update email sent to {user_email}")
            else:
                logger.error(f"Failed to send project update email to {user_email}")
                
        except Exception as e:
            logger.error(f"Project update email failed: {e}")
    
    async def send_voice_command_summary_email(self, user_email: str, user_name: str, 
                                             voice_commands: List[Dict[str, Any]], date: datetime):
        """
        Send daily voice command summary email.
        
        Args:
            user_email: User's email address
            user_name: User's name
            voice_commands: List of voice commands for the day
            date: Date of summary
        """
        try:
            subject = f"Voice Command Summary - {date.strftime('%B %d, %Y')}"
            
            # Generate HTML content for voice commands
            commands_html = ""
            for cmd in voice_commands:
                status_icon = "✅" if cmd.get("success") else "❌"
                commands_html += f"""
                <tr>
                    <td>{status_icon}</td>
                    <td>{cmd.get('transcription', 'N/A')}</td>
                    <td>{cmd.get('intent', 'N/A')}</td>
                    <td>{cmd.get('confidence', 0):.2f}</td>
                </tr>
                """
            
            html_content = f"""
            <html>
            <body>
                <h2>Voice Command Summary</h2>
                <p>Hello {user_name},</p>
                <p>Here's a summary of your voice commands for {date.strftime('%B %d, %Y')}:</p>
                
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Command</th>
                            <th>Intent</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        {commands_html}
                    </tbody>
                </table>
                
                <p>Total commands: {len(voice_commands)}</p>
                <p>Success rate: {sum(1 for cmd in voice_commands if cmd.get('success')) / len(voice_commands) * 100:.1f}%</p>
                
                <p>Best regards,<br>Voice AI Task Manager</p>
            </body>
            </html>
            """
            
            success = await self.send_email_notification(user_email, subject, html_content)
            
            if success:
                logger.info(f"Voice command summary email sent to {user_email}")
            else:
                logger.error(f"Failed to send voice command summary email to {user_email}")
                
        except Exception as e:
            logger.error(f"Voice command summary email failed: {e}")
    
    async def send_welcome_email(self, user_email: str, user_name: str):
        """
        Send welcome email to new users.
        
        Args:
            user_email: User's email address
            user_name: User's name
        """
        try:
            subject = "Welcome to Voice AI Task Manager"
            
            html_content = f"""
            <html>
            <body>
                <h2>Welcome to Voice AI Task Manager!</h2>
                <p>Hello {user_name},</p>
                <p>Welcome to the future of task management! You can now control your tasks and projects using just your voice.</p>
                
                <h3>Getting Started</h3>
                <ul>
                    <li>Try saying "Create a new task called buy groceries"</li>
                    <li>Say "Show my tasks" to see your current tasks</li>
                    <li>Use "Mark task as complete" to finish tasks</li>
                    <li>Say "Create a new project" to start a project</li>
                </ul>
                
                <h3>Voice Commands</h3>
                <p>Here are some voice commands you can try:</p>
                <ul>
                    <li>"Create task [task name]"</li>
                    <li>"Mark [task name] as complete"</li>
                    <li>"Show my tasks"</li>
                    <li>"Create project [project name]"</li>
                    <li>"Help" - to see all available commands</li>
                </ul>
                
                <p>Best regards,<br>The Voice AI Task Manager Team</p>
            </body>
            </html>
            """
            
            success = await self.send_email_notification(user_email, subject, html_content)
            
            if success:
                logger.info(f"Welcome email sent to {user_email}")
            else:
                logger.error(f"Failed to send welcome email to {user_email}")
                
        except Exception as e:
            logger.error(f"Welcome email failed: {e}")
    
    async def send_system_alert(self, user_id: str, title: str, message: str, 
                              priority: NotificationPriority = NotificationPriority.HIGH):
        """
        Send system alert notification.
        
        Args:
            user_id: User ID
            title: Alert title
            message: Alert message
            priority: Alert priority
        """
        try:
            notification = Notification(
                user_id=user_id,
                type=NotificationType.SYSTEM_ALERT,
                priority=priority,
                title=title,
                message=message,
                data={
                    "alert_type": "system",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Save to database
            logger.info(f"System alert created for user {user_id}: {title}")
            
        except Exception as e:
            logger.error(f"Failed to send system alert: {e}")
    
    async def mark_notification_as_read(self, notification_id: str, user_id: str) -> bool:
        """
        Mark notification as read.
        
        Args:
            notification_id: Notification ID
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would typically update the database
            # For now, just log the action
            logger.info(f"Notification {notification_id} marked as read by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")
            return False
    
    async def get_user_notifications(self, user_id: str, unread_only: bool = False, 
                                   limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user notifications.
        
        Args:
            user_id: User ID
            unread_only: Whether to return only unread notifications
            limit: Maximum number of notifications to return
            
        Returns:
            List of notification dictionaries
        """
        try:
            # This would typically query the database
            # For now, return mock data
            notifications = [
                {
                    "id": "mock_id_1",
                    "type": "task_created",
                    "title": "Task Created",
                    "message": "New task 'Buy groceries' has been created",
                    "read": False,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            ]
            
            if unread_only:
                notifications = [n for n in notifications if not n.get("read", False)]
            
            return notifications[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []
