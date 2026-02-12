"""
Notification Service
Handles multi-channel notifications (Push, SMS, Email, Voice)
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

import firebase_admin
from firebase_admin import credentials, messaging
from twilio.rest import Client as TwilioClient

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"
    VOICE = "voice"


class NotificationPriority(str, Enum):
    """Notification importance levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class PushNotificationService:
    """Firebase Cloud Messaging for push notifications"""
    
    def __init__(self, credentials_path: str = None):
        """Initialize FCM service"""
        try:
            if credentials_path and not firebase_admin._apps:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
            logger.info("Firebase Cloud Messaging initialized")
        except Exception as e:
            logger.warning(f"FCM initialization warning: {str(e)}")
    
    async def send_push(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> bool:
        """Send push notification via Firebase"""
        try:
            message = messaging.Message(
                token=device_token,
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                android=messaging.AndroidConfig(
                    priority="high" if priority == NotificationPriority.URGENT else "normal"
                ),
                apns=messaging.APNSConfig(
                    headers={"apns-priority": "10" if priority == NotificationPriority.URGENT else "10"}
                )
            )
            
            response = messaging.send(message)
            logger.info(f"Push notification sent: {response}")
            return True
        
        except Exception as e:
            logger.error(f"Push notification error: {str(e)}")
            return False


class SMSNotificationService:
    """Twilio SMS notification service"""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        """Initialize Twilio SMS service"""
        self.client = TwilioClient(account_sid, auth_token)
        self.from_number = from_number
        logger.info("Twilio SMS service initialized")
    
    async def send_sms(
        self,
        phone_number: str,
        message: str
    ) -> bool:
        """Send SMS via Twilio"""
        try:
            # Validate phone number format
            if not phone_number.startswith("+"):
                phone_number = f"+1{phone_number}"
            
            sms = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone_number
            )
            
            logger.info(f"SMS sent to {phone_number}: {sms.sid}")
            return True
        
        except Exception as e:
            logger.error(f"SMS error: {str(e)}")
            return False


class EmailNotificationService:
    """Email notification service"""
    
    def __init__(self, smtp_host: str, smtp_port: int, sender: str, password: str):
        """Initialize email service"""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender = sender
        self.password = password
        logger.info("Email notification service initialized")
    
    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send email notification"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender
            msg["To"] = recipient
            
            msg.attach(MIMEText(body, "plain"))
            if html_body:
                msg.attach(MIMEText(html_body, "html"))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.sendmail(self.sender, recipient, msg.as_string())
            
            logger.info(f"Email sent to {recipient}: {subject}")
            return True
        
        except Exception as e:
            logger.error(f"Email error: {str(e)}")
            return False


class VoiceNotificationService:
    """Twilio voice call notification service"""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str, twiml_url: str):
        """Initialize voice notification service"""
        self.client = TwilioClient(account_sid, auth_token)
        self.from_number = from_number
        self.twiml_url = twiml_url
        logger.info("Twilio voice notification service initialized")
    
    async def send_voice_call(
        self,
        phone_number: str,
        message_text: str
    ) -> bool:
        """Initiate voice call with message"""
        try:
            if not phone_number.startswith("+"):
                phone_number = f"+1{phone_number}"
            
            # Store message in session for TwiML to retrieve
            twiml_url_with_msg = f"{self.twiml_url}?message={message_text}"
            
            call = self.client.calls.create(
                to=phone_number,
                from_=self.from_number,
                url=twiml_url_with_msg
            )
            
            logger.info(f"Voice call initiated to {phone_number}: {call.sid}")
            return True
        
        except Exception as e:
            logger.error(f"Voice call error: {str(e)}")
            return False


class NotificationRouter:
    """Routes notifications based on staff preferences and urgency"""
    
    PRIORITY_CHANNELS = {
        NotificationPriority.LOW: [NotificationChannel.PUSH, NotificationChannel.EMAIL],
        NotificationPriority.NORMAL: [NotificationChannel.PUSH, NotificationChannel.SMS],
        NotificationPriority.HIGH: [NotificationChannel.SMS, NotificationChannel.PUSH],
        NotificationPriority.URGENT: [NotificationChannel.VOICE, NotificationChannel.SMS, NotificationChannel.PUSH],
    }
    
    @staticmethod
    async def get_preferred_channels(
        staff_member,
        priority: NotificationPriority
    ) -> List[NotificationChannel]:
        """Get notification channels for staff member based on priority"""
        
        # Parse staff preferences
        prefs = {}
        if staff_member.notification_preferences:
            try:
                import json
                prefs = json.loads(staff_member.notification_preferences)
            except:
                pass
        
        # Start with priority defaults
        channels = NotificationRouter.PRIORITY_CHANNELS.get(
            priority,
            [NotificationChannel.PUSH]
        ).copy()
        
        # Filter by staff availability
        if staff_member.availability_status.value == "on_break":
            # During break, prefer non-disruptive channels
            channels = [c for c in channels if c != NotificationChannel.VOICE]
        elif staff_member.availability_status.value == "off_duty":
            # Off duty, use less intrusive options
            channels = [NotificationChannel.PUSH, NotificationChannel.EMAIL]
        
        return channels


class NotificationService:
    """Main notification service orchestrator"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize notification service with config"""
        self.config = config
        
        # Initialize sub-services
        self.push_service = PushNotificationService(
            config.get("firebase_credentials_path")
        )
        
        twilio_config = config.get("twilio", {})
        self.sms_service = SMSNotificationService(
            account_sid=twilio_config.get("account_sid"),
            auth_token=twilio_config.get("auth_token"),
            from_number=twilio_config.get("phone_number")
        )
        
        email_config = config.get("email", {})
        self.email_service = EmailNotificationService(
            smtp_host=email_config.get("smtp_host") or "smtp.gmail.com",
            smtp_port=email_config.get("smtp_port") or 587,
            sender=email_config.get("sender_email"),
            password=email_config.get("sender_password")
        )
        
        self.voice_service = VoiceNotificationService(
            account_sid=twilio_config.get("account_sid"),
            auth_token=twilio_config.get("auth_token"),
            from_number=twilio_config.get("phone_number"),
            twiml_url=twilio_config.get("twiml_url", "")
        )
    
    async def notify_task_assigned(
        self,
        staff_member,
        task,
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> Dict[str, bool]:
        """Notify staff member of task assignment"""
        
        channels = await NotificationRouter.get_preferred_channels(
            staff_member, priority
        )
        
        results = {}
        
        for channel in channels:
            try:
                if channel == NotificationChannel.PUSH and staff_member.device_token:
                    results[channel.value] = await self.push_service.send_push(
                        device_token=staff_member.device_token,
                        title="New Task Assigned",
                        body=f"Priority {task.priority}: {task.description}",
                        data={
                            "task_id": task.id,
                            "priority": str(task.priority),
                            "location": task.location or "Unknown"
                        },
                        priority=priority
                    )
                
                elif channel == NotificationChannel.SMS and staff_member.phone_number:
                    results[channel.value] = await self.sms_service.send_sms(
                        phone_number=staff_member.phone_number,
                        message=f"Task assigned: {task.description} (Priority {task.priority})"
                    )
                
                elif channel == NotificationChannel.EMAIL and staff_member.email:
                    results[channel.value] = await self.email_service.send_email(
                        recipient=staff_member.email,
                        subject=f"Task Assigned: {task.description}",
                        body=f"A new task has been assigned:\n\nDescription: {task.description}\nPriority: {task.priority}\nLocation: {task.location or 'Unknown'}\nDue: {task.due_date}"
                    )
                
                elif channel == NotificationChannel.VOICE and staff_member.phone_number:
                    results[channel.value] = await self.voice_service.send_voice_call(
                        phone_number=staff_member.phone_number,
                        message_text=f"Urgent task assigned. {task.description}"
                    )
            
            except Exception as e:
                logger.error(f"Error sending {channel.value} notification: {str(e)}")
                results[channel.value] = False
        
        return results
    
    async def notify_task_completion(
        self,
        staff_member,
        task
    ) -> Dict[str, bool]:
        """Notify about task completion"""
        
        results = {}
        
        if staff_member.device_token:
            results["push"] = await self.push_service.send_push(
                device_token=staff_member.device_token,
                title="Task Completed",
                body=f"Your task has been marked complete: {task.description}",
                data={"task_id": task.id, "status": "completed"}
            )
        
        return results
    
    async def notify_urgent_escalation(
        self,
        recipients: List,
        escalation_reason: str
    ) -> bool:
        """Notify multiple staff of urgent escalation"""
        
        all_success = True
        
        for staff in recipients:
            channels = await NotificationRouter.get_preferred_channels(
                staff, NotificationPriority.URGENT
            )
            
            for channel in channels:
                try:
                    if channel == NotificationChannel.VOICE and staff.phone_number:
                        success = await self.voice_service.send_voice_call(
                            phone_number=staff.phone_number,
                            message_text=f"Urgent escalation: {escalation_reason}"
                        )
                        all_success = all_success and success
                
                    elif channel == NotificationChannel.SMS and staff.phone_number:
                        success = await self.sms_service.send_sms(
                            phone_number=staff.phone_number,
                            message=f"URGENT: {escalation_reason}"
                        )
                        all_success = all_success and success
                
                except Exception as e:
                    logger.error(f"Escalation notification error: {str(e)}")
                    all_success = False
        
        return all_success


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Notification Service module loaded successfully")
