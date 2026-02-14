"""
AI Communication Engine
Main FastAPI application for processing audio from VoIP and walkie-talkie sources
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import configparser
import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .models import init_db, get_session, Transcription, Task, AudioSource, IntentType
from .transcription_service import TranscriptionService, TranscriptionProvider
from .intent_classifier import IntentClassifier
from .task_action_engine import TaskActionEngine, TaskPrioritizer
from .notification_service import NotificationService, NotificationPriority
from .webhook_handlers import WebhookRouter, TwilioWebhookHandler, VonageWebhookHandler, WalkieTalkieWebhookHandler

logger = logging.getLogger(__name__)


class AudioStreamRequest(BaseModel):
    """Incoming audio stream request"""
    caller_id: str
    source: AudioSource
    audio_data: bytes = Field(..., description="Base64 encoded audio data")
    speaker_name: Optional[str] = None
    channel: Optional[str] = None


class TranscriptionResponse(BaseModel):
    """Transcription API response"""
    transcription_id: str
    text: str
    confidence: float
    intent_type: IntentType
    priority: int
    assigned_to: Optional[str] = None
    location: Optional[str] = None


class AudioStreamManager:
    """Manages concurrent audio streams"""
    
    def __init__(self, max_streams: int = 50):
        self.max_streams = max_streams
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.semaphore = asyncio.Semaphore(max_streams)
    
    async def add_stream(self, stream_id: str, source: AudioSource) -> bool:
        """Add new audio stream"""
        if len(self.active_streams) >= self.max_streams:
            logger.warning(f"Max stream limit reached ({self.max_streams})")
            return False
        
        self.active_streams[stream_id] = {
            "source": source,
            "started_at": datetime.utcnow(),
            "audio_chunks": []
        }
        logger.info(f"Stream {stream_id} added (Total: {len(self.active_streams)})")
        return True
    
    async def remove_stream(self, stream_id: str) -> Dict[str, Any]:
        """Remove audio stream and return data"""
        stream = self.active_streams.pop(stream_id, None)
        if stream:
            stream["duration"] = (datetime.utcnow() - stream["started_at"]).total_seconds()
            logger.info(f"Stream {stream_id} removed (Duration: {stream['duration']:.2f}s)")
        return stream or {}
    
    async def add_chunk(self, stream_id: str, chunk: bytes) -> bool:
        """Add audio chunk to stream"""
        if stream_id not in self.active_streams:
            return False
        self.active_streams[stream_id]["audio_chunks"].append(chunk)
        return True
    
    def get_stream_info(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get stream information"""
        return self.active_streams.get(stream_id)
    
    def get_all_streams(self) -> List[Dict[str, Any]]:
        """Get all active streams"""
        return list(self.active_streams.values())


class CommunicationMiddleware:
    """Main orchestrator for communication pipeline"""
    
    def __init__(self, config: configparser.ConfigParser):
        """Initialize middleware with configuration"""
        self.config = config
        
        # Initialize services
        self.transcription_service = TranscriptionService(
            provider=config.get("transcription", "provider", fallback="huggingface_whisper"),
            api_key=config.get("openai", "api_key", fallback=None),
            model=config.get("transcription", "model", fallback="openai/whisper-tiny"),
            language=config.get("transcription", "language", fallback="en"),
            timeout_ms=int(config.get("transcription", "timeout", fallback="2000"))
        )
        
        self.intent_classifier = IntentClassifier(
            provider=config.get("llm", "provider", fallback="huggingface"),
            model=config.get("llm", "model", fallback="facebook/bart-large-mnli"),
            temperature=float(config.get("llm", "temperature", fallback="0.7")),
            max_tokens=int(config.get("llm", "max_tokens", fallback="500"))
        )
        
        self.notification_service = NotificationService(
            config=self._build_notification_config()
        )
        
        self.stream_manager = AudioStreamManager(
            max_streams=int(config.get("performance", "max_concurrent_streams", fallback="50"))
        )
        
        logger.info("CommunicationMiddleware initialized")
    
    def _build_notification_config(self) -> Dict[str, Any]:
        """Build notification configuration"""
        return {
            "firebase_credentials_path": self.config.get("firebase", "credentials_path", fallback=None),
            "twilio": {
                "account_sid": self.config.get("twilio", "account_sid"),
                "auth_token": self.config.get("twilio", "auth_token"),
                "phone_number": self.config.get("twilio", "phone_number"),
                "twiml_url": self.config.get("twilio", "webhook_url", fallback="")
            },
            "email": {
                "smtp_host": self.config.get("email", "smtp_host", fallback="smtp.gmail.com"),
                "smtp_port": int(self.config.get("email", "smtp_port", fallback="587")),
                "sender_email": self.config.get("email", "sender_email"),
                "sender_password": self.config.get("email", "sender_password")
            }
        }
    
    async def process_audio_stream(
        self,
        caller_id: str,
        audio_data: bytes,
        source: AudioSource,
        db_session: Session
    ) -> Dict[str, Any]:
        """
        Main processing pipeline
        
        Flow: Audio -> Transcription -> Intent Classification -> Task Creation -> Notification
        """
        
        try:
            # Step 1: Transcribe
            logger.info(f"Processing audio from {caller_id} ({source.value})")
            transcription_result = await self.transcription_service.transcribe_audio(
                audio_data=audio_data,
                speaker_id=caller_id
            )
            
            if not transcription_result:
                raise Exception("Transcription failed")
            
            # Save transcription to database
            transcription = Transcription(
                source=source,
                raw_text=transcription_result.text,
                confidence_score=transcription_result.confidence,
                speaker_id=caller_id,
                processing_timestamp=datetime.utcnow()
            )
            db_session.add(transcription)
            db_session.commit()
            
            logger.info(f"Transcription saved: {transcription.id}")
            
            # Step 2: Classify intent
            classification = await self.intent_classifier.classify(
                text=transcription_result.text,
                speaker_id=caller_id
            )
            
            transcription.intent_type = classification.primary_intent
            transcription.requires_human_review = classification.requires_human_review
            db_session.commit()
            
            logger.info(f"Intent classified: {classification.primary_intent.value}")
            
            # Step 3: Create task if applicable
            task = None
            if classification.primary_intent in [IntentType.TASK, IntentType.URGENT]:
                engine = TaskActionEngine(db_session)
                task = await engine.create_task_from_transcription(
                    transcription=transcription,
                    intent_classification={
                        "primary_intent": classification.primary_intent.value,
                        "reasoning": classification.reasoning
                    },
                    extracted_entities=classification.extracted_entities
                )
                
                if task:
                    logger.info(f"Task created: {task.id}")
                    
                    # Step 4: Notify assigned staff
                    if task.assigned_to:
                        staff_member = db_session.query(
                            __import__('models').StaffMember
                        ).filter_by(id=task.assigned_to).first()
                        
                        if staff_member:
                            priority = NotificationPriority.URGENT if task.priority >= 4 else NotificationPriority.NORMAL
                            await self.notification_service.notify_task_assigned(
                                staff_member=staff_member,
                                task=task,
                                priority=priority
                            )
            
            return {
                "status": "success",
                "transcription_id": transcription.id,
                "text": transcription_result.text,
                "confidence": transcription_result.confidence,
                "intent": classification.primary_intent.value,
                "priority": task.priority if task else 1,
                "task_id": task.id if task else None,
                "requires_human_review": classification.requires_human_review
            }
        
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            db_session.rollback()
            return {
                "status": "error",
                "error": str(e)
            }


# Initialize FastAPI app
app = FastAPI(
    title="AI Communication Engine",
    description="Real-time voice/radio processing middleware",
    version="1.0.0"
)

# Initialize database
init_db()

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")

# Initialize middleware
middleware = CommunicationMiddleware(config)

# Initialize webhook handlers
twilio_handler = TwilioWebhookHandler(config.get("twilio", "auth_token", fallback=""))
vonage_handler = VonageWebhookHandler(
    api_key=config.get("vonage", "api_key", fallback=""),
    api_secret=config.get("vonage", "api_secret", fallback="")
)
walkie_talkie_handler = WalkieTalkieWebhookHandler(
    api_key=config.get("walkie_talkie", "api_key", fallback="")
)
webhook_router = WebhookRouter(
    twilio_handler=twilio_handler,
    vonage_handler=vonage_handler,
    walkie_talkie_handler=walkie_talkie_handler
)


# ==================== REST API Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Communication Engine",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/transcribe")
async def transcribe_audio(request: AudioStreamRequest, background_tasks: BackgroundTasks):
    """Transcribe audio and process through pipeline"""
    
    db = next(get_session())
    try:
        result = await middleware.process_audio_stream(
            caller_id=request.caller_id,
            audio_data=request.audio_data,
            source=request.source,
            db_session=db
        )
        
        return TranscriptionResponse(**result) if result["status"] == "success" else result
    finally:
        db.close()


@app.post("/webhooks/twilio")
async def twilio_webhook(request: Request):
    """Twilio incoming call/SMS webhook"""
    
    data = await request.form()
    signature = request.headers.get("X-Twilio-Signature", "")
    
    try:
        # Validate signature
        is_valid = await twilio_handler.validate_webhook(
            dict(data),
            signature,
            str(request.url)
        )
        
        if not is_valid:
            logger.warning("Invalid Twilio signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Process webhook
        result = await webhook_router.route_webhook("twilio", dict(data), signature)
        
        logger.info(f"Twilio webhook processed: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Twilio webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/webhooks/vonage")
async def vonage_webhook(request: Request):
    """Vonage incoming SMS/call webhook"""
    
    data = await request.json()
    
    try:
        is_valid = await vonage_handler.validate_webhook(data)
        
        if not is_valid:
            logger.warning("Invalid Vonage signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        result = await webhook_router.route_webhook("vonage", data)
        
        logger.info(f"Vonage webhook processed: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Vonage webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/webhooks/walkie-talkie")
async def walkie_talkie_webhook(request: Request):
    """Walkie-talkie transmission webhook"""
    
    data = await request.json()
    signature = request.headers.get("X-Signature", "")
    
    try:
        is_valid = await walkie_talkie_handler.validate_webhook(data, signature)
        
        if not is_valid:
            logger.warning("Invalid walkie-talkie signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        result = await webhook_router.route_webhook("walkie_talkie", data, signature)
        
        logger.info(f"Walkie-talkie webhook processed: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Walkie-talkie webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.get("/streams")
async def get_active_streams():
    """Get active audio streams"""
    return {
        "active_streams": len(middleware.stream_manager.active_streams),
        "max_streams": middleware.stream_manager.max_streams,
        "current": middleware.stream_manager.get_all_streams()
    }


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task details"""
    db = next(get_session())
    try:
        task = db.query(Task).filter_by(id=task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "id": task.id,
            "description": task.description,
            "priority": task.priority,
            "status": task.status.value,
            "location": task.location,
            "assigned_to": task.assigned_to,
            "created_at": task.created_at.isoformat(),
            "due_date": task.due_date.isoformat() if task.due_date else None
        }
    finally:
        db.close()


@app.put("/tasks/{task_id}/status")
async def update_task_status(task_id: str, new_status: str):
    """Update task status"""
    db = next(get_session())
    try:
        task = db.query(Task).filter_by(id=task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Import TaskStatus here to avoid circular imports
        from .models import TaskStatus
        
        task.status = TaskStatus[new_status.upper()]
        if new_status.upper() == "COMPLETED":
            task.completed_at = datetime.utcnow()
        
        db.commit()
        return {"status": "success", "task_id": task_id, "new_status": new_status}
    finally:
        db.close()


# ==================== WebSocket Endpoint (Real-time Streaming) ====================

@app.websocket("/ws/audio/{caller_id}")
async def websocket_audio_stream(websocket: WebSocket, caller_id: str):
    """WebSocket endpoint for real-time audio streaming"""
    await websocket.accept()
    
    stream_id = f"{caller_id}_{datetime.utcnow().timestamp()}"
    success = await middleware.stream_manager.add_stream(stream_id, AudioSource.VOIP_PHONE)
    
    if not success:
        await websocket.send_json({
            "error": "Max stream limit reached",
            "max_streams": middleware.stream_manager.max_streams
        })
        await websocket.close()
        return
    
    try:
        while True:
            # Receive audio chunk
            data = await websocket.receive_bytes()
            
            if not data:
                break
            
            # Add to stream
            await middleware.stream_manager.add_chunk(stream_id, data)
            
            # Send acknowledgement
            await websocket.send_json({"status": "chunk_received", "size": len(data)})
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    
    finally:
        await middleware.stream_manager.remove_stream(stream_id)
        logger.info(f"WebSocket closed for caller {caller_id}")


if __name__ == "__main__":
    import uvicorn
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    host = config.get("websocket", "host", fallback="0.0.0.0")
    port = int(config.get("websocket", "port", fallback="8000"))
    
    print(f"Starting AI Communication Engine on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
