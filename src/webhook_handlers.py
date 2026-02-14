"""
Webhook Handlers
Handles incoming webhooks from Twilio, Vonage, and walkie-talkie systems
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from abc import ABC, abstractmethod
import json

logger = logging.getLogger(__name__)


class WebhookHandler(ABC):
    """Base webhook handler"""
    
    @abstractmethod
    async def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook"""
        pass
    
    @abstractmethod
    async def validate_webhook(self, data: Dict[str, Any], signature: str) -> bool:
        """Validate webhook authenticity"""
        pass


class TwilioWebhookHandler(WebhookHandler):
    """Handles Twilio voice and SMS webhooks"""
    
    def __init__(self, auth_token: str):
        """Initialize Twilio webhook handler"""
        self.auth_token = auth_token
        logger.info("Twilio webhook handler initialized")
    
    async def validate_webhook(
        self,
        data: Dict[str, Any],
        signature: str,
        request_url: str
    ) -> bool:
        """
        Validate Twilio webhook signature
        """
        try:
            from twilio.request_validator import RequestValidator
            validator = RequestValidator(self.auth_token)
            return validator.validate(request_url, data, signature)
        except Exception as e:
            logger.error(f"Twilio signature validation error: {str(e)}")
            return False
    
    async def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Twilio webhook (call or SMS)"""
        
        webhook_type = self._determine_webhook_type(data)
        logger.info(f"Processing Twilio {webhook_type} webhook")
        
        if webhook_type == "call":
            return await self._process_call_webhook(data)
        elif webhook_type == "sms":
            return await self._process_sms_webhook(data)
        elif webhook_type == "recording":
            return await self._process_recording_webhook(data)
        else:
            return {"status": "unknown_webhook_type"}
    
    def _determine_webhook_type(self, data: Dict[str, Any]) -> str:
        """Determine webhook type from data"""
        if "RecordingUrl" in data or "RecordingSid" in data:
            return "recording"
        elif "From" in data and "Body" in data:
            return "sms"
        elif "CallSid" in data:
            return "call"
        return "unknown"
    
    async def _process_call_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming or status call webhook"""
        
        return {
            "status": "success",
            "webhook_type": "call",
            "call_sid": data.get("CallSid"),
            "from": data.get("From"),
            "to": data.get("To"),
            "call_status": data.get("CallStatus"),
            "direction": data.get("Direction"),
            "timestamp": datetime.utcnow().isoformat(),
            "action": "stream" if data.get("CallStatus") == "ringing" else "log"
        }
    
    async def _process_sms_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming SMS webhook"""
        
        return {
            "status": "success",
            "webhook_type": "sms",
            "sms_sid": data.get("MessageSid"),
            "from": data.get("From"),
            "to": data.get("To"),
            "body": data.get("Body"),
            "num_media": int(data.get("NumMedia", 0)),
            "timestamp": datetime.utcnow().isoformat(),
            "requires_transcription": True
        }
    
    async def _process_recording_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process call recording webhook"""
        
        return {
            "status": "success",
            "webhook_type": "recording",
            "recording_sid": data.get("RecordingSid"),
            "call_sid": data.get("CallSid"),
            "recording_url": data.get("RecordingUrl"),
            "recording_duration": int(data.get("RecordingDuration", 0)),
            "timestamp": datetime.utcnow().isoformat(),
            "action": "transcribe"
        }


class VonageWebhookHandler(WebhookHandler):
    """Handles Vonage (Nexmo) voice and SMS webhooks"""
    
    def __init__(self, api_key: str, api_secret: str):
        """Initialize Vonage webhook handler"""
        self.api_key = api_key
        self.api_secret = api_secret
        logger.info("Vonage webhook handler initialized")
    
    async def validate_webhook(
        self,
        data: Dict[str, Any],
        signature: str = None
    ) -> bool:
        """
        Validate Vonage webhook signature
        """
        try:
            import hmac
            import hashlib
            
            # Vonage uses MD5 hash of sorted params + API secret
            if not signature:
                signature = data.pop("sig", "")
            
            # Sort and concatenate params
            params_str = "&".join(
                f"{k}={v}" for k, v in sorted(data.items())
            ) + self.api_secret
            
            expected_sig = hashlib.md5(params_str.encode()).hexdigest()
            return signature == expected_sig
        
        except Exception as e:
            logger.error(f"Vonage signature validation error: {str(e)}")
            return False
    
    async def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Vonage webhook"""
        
        webhook_type = data.get("type")
        logger.info(f"Processing Vonage {webhook_type} webhook")
        
        if webhook_type == "mo-sms":
            return await self._process_sms_webhook(data)
        elif webhook_type == "inbound-call":
            return await self._process_call_webhook(data)
        elif webhook_type == "recording":
            return await self._process_recording_webhook(data)
        else:
            return {"status": "unknown_webhook_type"}
    
    async def _process_sms_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming SMS webhook"""
        
        return {
            "status": "success",
            "webhook_type": "sms",
            "message_id": data.get("messageId"),
            "from": data.get("msisdn"),
            "to": data.get("to"),
            "text": data.get("text"),
            "timestamp": datetime.utcnow().isoformat(),
            "requires_transcription": True
        }
    
    async def _process_call_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process inbound call webhook"""
        
        return {
            "status": "success",
            "webhook_type": "call",
            "call_id": data.get("uuid"),
            "from": data.get("from"),
            "to": data.get("to"),
            "conversation_uuid": data.get("conversation_uuid"),
            "timestamp": datetime.utcnow().isoformat(),
            "action": "stream"
        }
    
    async def _process_recording_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process call recording webhook"""
        
        return {
            "status": "success",
            "webhook_type": "recording",
            "recording_url": data.get("recording_url"),
            "call_uuid": data.get("uuid"),
            "recording_duration": int(data.get("recording_duration", 0)),
            "timestamp": datetime.utcnow().isoformat(),
            "action": "transcribe"
        }


class WalkieTalkieWebhookHandler(WebhookHandler):
    """Handles walkie-talkie radio communication webhooks"""
    
    def __init__(self, api_key: str):
        """Initialize walkie-talkie webhook handler"""
        self.api_key = api_key
        logger.info("Walkie-talkie webhook handler initialized")
    
    async def validate_webhook(
        self,
        data: Dict[str, Any],
        signature: str
    ) -> bool:
        """
        Validate walkie-talkie webhook signature
        """
        try:
            import hmac
            import hashlib
            
            payload = json.dumps(data, sort_keys=True)
            expected_sig = hmac.new(
                self.api_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return signature == expected_sig
        
        except Exception as e:
            logger.error(f"Walkie-talkie signature validation error: {str(e)}")
            return False
    
    async def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process walkie-talkie webhook"""
        
        webhook_type = data.get("event_type")
        logger.info(f"Processing walkie-talkie {webhook_type} webhook")
        
        if webhook_type == "transmission_received":
            return await self._process_transmission_webhook(data)
        elif webhook_type == "device_status":
            return await self._process_device_status_webhook(data)
        elif webhook_type == "channel_activity":
            return await self._process_channel_activity_webhook(data)
        else:
            return {"status": "unknown_webhook_type"}
    
    async def _process_transmission_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process radio transmission webhook"""
        
        return {
            "status": "success",
            "webhook_type": "transmission",
            "transmission_id": data.get("transmission_id"),
            "device_id": data.get("device_id"),
            "channel": data.get("channel"),
            "audio_url": data.get("audio_url"),
            "duration_seconds": float(data.get("duration", 0)),
            "signal_strength": data.get("signal_strength"),
            "timestamp": datetime.utcnow().isoformat(),
            "requires_transcription": True
        }
    
    async def _process_device_status_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process device status webhook"""
        
        return {
            "status": "success",
            "webhook_type": "device_status",
            "device_id": data.get("device_id"),
            "device_name": data.get("device_name"),
            "online_status": data.get("online_status"),
            "battery_level": int(data.get("battery_level", 0)),
            "location": data.get("location"),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _process_channel_activity_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process channel activity webhook"""
        
        return {
            "status": "success",
            "webhook_type": "channel_activity",
            "channel": data.get("channel"),
            "activity_type": data.get("activity_type"),
            "timestamp": datetime.utcnow().isoformat()
        }


class WebhookRouter:
    """Routes webhooks to appropriate handlers"""
    
    def __init__(
        self,
        twilio_handler: TwilioWebhookHandler = None,
        vonage_handler: VonageWebhookHandler = None,
        walkie_talkie_handler: WalkieTalkieWebhookHandler = None
    ):
        """Initialize webhook router"""
        self.twilio_handler = twilio_handler
        self.vonage_handler = vonage_handler
        self.walkie_talkie_handler = walkie_talkie_handler
    
    async def route_webhook(
        self,
        source: str,
        data: Dict[str, Any],
        signature: str = None
    ) -> Dict[str, Any]:
        """
        Route webhook to appropriate handler
        
        Args:
            source: "twilio", "vonage", or "walkie_talkie"
            data: Webhook payload
            signature: Webhook signature for validation
            
        Returns:
            Processed webhook response
        """
        
        if source == "twilio" and self.twilio_handler:
            return await self.twilio_handler.process_webhook(data)
        
        elif source == "vonage" and self.vonage_handler:
            return await self.vonage_handler.process_webhook(data)
        
        elif source == "walkie_talkie" and self.walkie_talkie_handler:
            return await self.walkie_talkie_handler.process_webhook(data)
        
        else:
            logger.warning(f"Unknown webhook source: {source}")
            return {"status": "unknown_source"}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Webhook Handlers module loaded successfully")
