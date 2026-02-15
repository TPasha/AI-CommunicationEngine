from __future__ import annotations

import os
import sys
import json
from typing import Optional
import sqlite3
from datetime import datetime

# Ensure parent project path is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .intent_classifier import IntentClassifier, IntentType

app = FastAPI(title="AI Communication Engine - MVP", version="0.1.0")

classifier = IntentClassifier()

# Mount static files and templates
web_dir = os.path.join(ROOT, "web")
static_dir = os.path.join(web_dir, "static")
if os.path.isdir(static_dir):
    app.mount("/mvp/static", StaticFiles(directory=static_dir), name="mvp_static")
    
templates_dir = os.path.join(web_dir, "templates")
if os.path.isdir(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)

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
