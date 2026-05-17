from __future__ import annotations

import os
import sys
import json
import logging
from typing import Optional
import sqlite3
from datetime import datetime
from io import BytesIO
import mimetypes
import uuid

try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

logger = logging.getLogger(__name__)

# Ensure parent project path is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi import FastAPI, Request, BackgroundTasks, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .intent_classifier import IntentClassifier, IntentType
from .transcription_service import TranscriptionService, TranscriptionProvider

app = FastAPI(title="AI Communication Engine - MVP", version="0.1.0")

# Initialize classifier lazily (don't load on startup to avoid memory issues)
classifier = None

transcription_service = TranscriptionService(
    provider="huggingface_whisper",
    model="openai/whisper-large-v3-turbo",
    language="auto",
    timeout_ms=30000
)

# Lightweight Zero-Shot Classifier for task categorization
zero_shot_classifier = None
OPERATIONAL_TEAMS = ["Kitchen", "Housekeeping", "Maintenance", "Front Desk", "Security", "Room Service", "Concierge"]

def get_zero_shot_classifier():
    global zero_shot_classifier
    if zero_shot_classifier is None and HAS_TRANSFORMERS:
        logger.info("Initializing lightweight zero-shot classifier (valhalla/distilbart-mnli-12-1)...")
        zero_shot_classifier = pipeline(
            "zero-shot-classification",
            model="valhalla/distilbart-mnli-12-1"
        )
    return zero_shot_classifier

# Mount static files and templates
web_dir = os.path.join(ROOT, "web")
static_dir = os.path.join(web_dir, "static")
if os.path.isdir(static_dir):
    app.mount("/mvp/static", StaticFiles(directory=static_dir), name="mvp_static")
    
templates_dir = os.path.join(web_dir, "templates")
if os.path.isdir(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)

# Create and mount audio directory for storing voice requests
audio_dir = os.path.join(ROOT, "data", "audio")
os.makedirs(audio_dir, exist_ok=True)
app.mount("/mvp/audio", StaticFiles(directory=audio_dir), name="mvp_audio")

# Simple in-memory pub/sub for notifications (SSE)
import asyncio
from typing import List

_subscribers: List[asyncio.Queue] = []

async def _publish(message: str):
    for q in list(_subscribers):
        try:
            await q.put(message)
        except Exception:
            # ignore subscriber errors
            pass


# Simple SQLite persistence for notifications
DB_PATH = os.path.join(ROOT, "web", "mvp_notifications.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def _get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _init_db():
    conn = _get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def persist_notification(obj: dict):
    try:
        conn = _get_db_connection()
        cur = conn.cursor()
        nid = obj.get("id") or f"notif-{int(datetime.utcnow().timestamp()*1000)}"
        cur.execute(
            "INSERT OR REPLACE INTO notifications (id, payload, created_at) VALUES (?, ?, ?)",
            (nid, json.dumps(obj), datetime.utcnow().isoformat())
        )
        conn.commit()
    finally:
        conn.close()


def fetch_notifications(limit: int = 100):
    conn = _get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, payload, created_at FROM notifications ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    result = []
    for r in rows:
        try:
            payload = json.loads(r["payload"])
        except Exception:
            payload = {"raw": r["payload"]}
        result.append({"id": r["id"], "payload": payload, "created_at": r["created_at"]})
    conn.close()
    return result


# initialize DB on import
_init_db()


class ProcessRequest(BaseModel):
    text: str
    speaker_id: Optional[str] = None


@app.get("/mvp/health")
async def health():
    return {"status": "healthy", "component": "mvp"}


@app.post("/mvp/process")
async def process(req: ProcessRequest):
    """Process text through the existing `IntentClassifier` and return a simple task POC."""
    classification = await classifier.classify(req.text, req.speaker_id)

    result = {
        "classification": classification.to_dict(),
        "requires_human_review": classification.requires_human_review,
    }

    # Simple task creation POC
    intent_value = classification.intent_type.value if hasattr(classification, 'intent_type') else None
    if intent_value in (IntentType.TASK.value, IntentType.URGENT.value, IntentType.ESCALATION.value):
        task = {
            "id": "mvp-task-1",
            "description": classification.primary_intent,
            "priority": classification.suggested_priority,
            "extracted_entities": classification.extracted_entities,
        }
        result["task"] = task
    else:
        result["task"] = None

    return {"status": "ok", "result": result}


@app.post("/mvp/voice")
async def process_voice(file: UploadFile = File(...), speaker_id: Optional[str] = None):
    """
    Process voice input: transcribe audio and classify intent.
    Accepts: WAV, MP3, OGG, M4A
    """
    try:
        # Read audio file
        audio_data = await file.read()
        logger.info(f"[VOICE] Received audio file: {file.filename}, size: {len(audio_data)} bytes")
        
        # Validate audio data
        if not audio_data or len(audio_data) < 100:
            logger.error("[VOICE] Audio data too small or empty")
            return JSONResponse(
                {"status": "error", "message": "Audio file is too small or empty"},
                status_code=400
            )
        
        # Transcribe audio
        logger.info("[VOICE] Starting transcription...")
        result = await transcription_service.transcribe_audio(
            audio_data=audio_data,
            speaker_id=speaker_id or "voice_user"
        )
        
        logger.info(f"[VOICE] Transcription result: {result}")
        
        if not result or not result.text or not result.text.strip():
            logger.error("[VOICE] Transcription returned empty text")
            return JSONResponse(
                {"status": "error", "message": "Could not transcribe audio - no speech detected"},
                status_code=400
            )
        
        text = result.text
        
        # Save audio file
        filename = f"voice_{int(datetime.utcnow().timestamp()*1000)}_{uuid.uuid4().hex[:6]}.wav"
        filepath = os.path.join(audio_dir, filename)
        with open(filepath, "wb") as f:
            f.write(audio_data)
            
        audio_url = f"/mvp/audio/{filename}"
        
        # Run classification
        team_category = "General"
        intent = "ORDER"
        confidence = 0.5
        requires_human_review = True
        
        classifier_pipeline = get_zero_shot_classifier()
        if classifier_pipeline:
            try:
                clf_result = classifier_pipeline(text, OPERATIONAL_TEAMS)
                team_category = clf_result["labels"][0]
                confidence = clf_result["scores"][0]
                requires_human_review = confidence < 0.6
                logger.info(f"[VOICE] Classified as {team_category} with {confidence:.2f} confidence")
            except Exception as e:
                logger.error(f"[VOICE] Zero-shot classification failed: {str(e)}")
        
        return {
            "status": "ok",
            "transcription": text,
            "classification": {
                "primary_intent": intent,
                "confidence": confidence,
                "intent_type": intent
            },
            "intent": intent,
            "requires_human_review": requires_human_review,
            "task": {
                "id": f"task-voice-{int(datetime.utcnow().timestamp()*1000)}",
                "description": text,
                "priority": "high" if "urgent" in text.lower() or "emergency" in text.lower() else "normal",
                "transcription": text,
                "team_category": team_category,
                "audio_url": audio_url,
                "confidence": confidence
            }
        }
        
    except Exception as e:
        logger.error(f"Voice processing error: {str(e)}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


@app.post("/mvp/notify")
async def notify(payload: dict, background_tasks: BackgroundTasks):
    """Receive a notification (e.g., a created task) and publish to connected UI clients."""
    # persist and publish
    try:
        persist_notification(payload)
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

    message = json.dumps(payload)
    background_tasks.add_task(_publish, message)
    return JSONResponse({"status": "published"})


@app.get("/mvp/history")
async def history(limit: int = 100):
    """Return historical notifications from the lightweight store."""
    items = fetch_notifications(limit)
    return {"count": len(items), "items": items}


@app.get("/mvp/stream")
async def stream():
    """SSE stream endpoint clients can subscribe to for notifications."""
    queue: asyncio.Queue = asyncio.Queue()
    _subscribers.append(queue)

    async def event_generator(q: asyncio.Queue):
        try:
            while True:
                data = await q.get()
                yield f"data: {data}\n\n"
        finally:
            # cleanup when client disconnects
            try:
                _subscribers.remove(q)
            except ValueError:
                pass

    return StreamingResponse(event_generator(queue), media_type="text/event-stream")


def _load_index_html():
    """Load index.html with proper UTF-8 encoding."""
    templates_dir = os.path.join(ROOT, "web", "templates")
    index_path = os.path.join(templates_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>AI Communication Engine</h1></body></html>"


@app.get("/")
@app.get("/mvp")
async def root():
    """Serve the AI Command Center dashboard at root and /mvp."""
    html_content = _load_index_html()
    return HTMLResponse(content=html_content)


@app.get("/mvp/ui")
async def ui(request: Request):
    """Serve the AI Command Center React dashboard."""
    html_content = _load_index_html()
    return HTMLResponse(content=html_content)


# Catch-all for paths under /mvp
@app.get("/mvp/{full_path:path}")
async def catch_all(full_path: str):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "path": f"/mvp/{full_path}",
            "available_endpoints": ["/", "/mvp", "/mvp/ui", "/mvp/health", "/mvp/stream", "/mvp/notify", "/mvp/history"]
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.web_app:app", host="127.0.0.1", port=8800, reload=True)
