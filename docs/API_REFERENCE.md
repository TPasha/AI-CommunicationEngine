# AI Command Center - API Reference for Developers

## Quick Start

**Server**: `http://localhost:8800`

### Core Endpoints

| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| GET | `/` | Serve dashboard | HTML (React app) |
| GET | `/mvp` | Dashboard alias | HTML (React app) |
| GET | `/mvp/ui` | Dashboard explicit | HTML (React app) |
| GET | `/mvp/health` | Service status | `{"status": "healthy", "component": "mvp"}` |
| POST | `/mvp/notify` | Send task notification | `{"status": "published"}` |
| GET | `/mvp/history` | Get historical tasks | `{"count": N, "items": [...]}` |
| GET | `/mvp/stream` | SSE stream (tasks) | Event stream (text/event-stream) |
| POST | `/mvp/process` | Process audio text | Classification result |

---

## Broadcasting Tasks to Dashboard

### POST `/mvp/notify`

Send a task notification that will appear in real-time on all connected dashboards.

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "id": "task-unique-id-or-auto-generated",
  "description": "What the operator said or task description",
  "intent": "ORDER",
  "priority": "high",
  "extracted_entities": {
    "item": "Forklift B",
    "location": "Bay 4"
  },
  "requires_human_review": false
}
```

**Response (Success)**:
```json
{
  "status": "published"
}
```

**Response (Error)**:
```json
{
  "status": "error",
  "error": "error message"
}
```

**Example (curl)**:
```bash
curl -X POST http://localhost:8800/mvp/notify \
  -H "Content-Type: application/json" \
  -d '{
    "id": "op-2026-02-14-001",
    "description": "Equipment transport needed from Warehouse to Bay 3",
    "intent": "ORDER",
    "priority": "normal",
    "extracted_entities": {
      "item": "Pallet Jack",
      "location": "Bay 3"
    },
    "requires_human_review": false
  }'
```

**Example (Python)**:
```python
import requests
import json

payload = {
    "id": "task-12345",
    "description": "Emergency breakdown at Zone A",
    "intent": "EMERGENCY",
    "priority": "high",
    "extracted_entities": {
        "item": "Equipment X",
        "location": "Zone A"
    },
    "requires_human_review": True
}

response = requests.post(
    "http://localhost:8800/mvp/notify",
    json=payload,
    headers={"Content-Type": "application/json"}
)

print(response.json())
# Output: {"status": "published"}
```

**Example (Node.js)**:
```javascript
fetch('http://localhost:8800/mvp/notify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        id: 'task-789',
        description: 'Inventory check needed',
        intent: 'INQUIRY',
        priority: 'low',
        extracted_entities: {
            item: 'Inventory Box',
            location: 'Storage'
        },
        requires_human_review: false
    })
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## Receiving Real-Time Updates (Browser)

### GET `/mvp/stream` (Server-Sent Events)

Subscribe to live task notifications using EventSource API (automatic from React app).

**JavaScript (Manual Subscribe)**:
```javascript
const eventSource = new EventSource('/mvp/stream');

eventSource.onmessage = (event) => {
    const task = JSON.parse(event.data);
    console.log('New task:', task);
    
    // Handle task display
    // {
    //   "id": "task-123",
    //   "description": "...",
    //   "intent": "ORDER",
    //   "priority": "normal",
    //   "extracted_entities": {...},
    //   "requires_human_review": false
    // }
};

eventSource.onerror = () => {
    console.log('SSE connection error');
    eventSource.close();
};

// Clean up when done
// eventSource.close();
```

**Behavior**:
- Auto-reconnects on network loss
- Sends only newly published tasks
- No historical data (use `/mvp/history` for that)
- Lightweight protocol (HTTP long-polling)

---

## Fetching Historical Tasks

### GET `/mvp/history?limit=100`

Retrieve previously published tasks from persistent storage.

**Query Parameters**:
- `limit` (optional, default: 100): Number of tasks to return

**Response**:
```json
{
  "count": 5,
  "items": [
    {
      "id": "task-001",
      "payload": {
        "id": "task-001",
        "description": "First task received",
        "intent": "ORDER",
        ...
      },
      "created_at": "2026-02-14T14:23:45.123456"
    },
    ...
  ]
}
```

**Example (Python)**:
```python
import requests

response = requests.get('http://localhost:8800/mvp/history?limit=50')
data = response.json()

for item in data['items']:
    task = item['payload']
    print(f"ID: {task['id']}, Intent: {task['intent']}")
```

---

## Processing Text Through Intent Classifier

### POST `/mvp/process`

Classify voice transcription as intent and extract entities (requires OpenAI API key).

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "text": "I need a forklift to move pallets to bay 4",
  "speaker_id": "operator-001"
}
```

**Response**:
```json
{
  "status": "ok",
  "result": {
    "classification": {
      "intent_type": "task",
      "primary_intent": "Equipment request",
      "suggested_priority": "normal",
      "confidence_score": 0.92,
      "extracted_entities": {
        "equipment": "forklift",
        "location": "bay 4"
      }
    },
    "requires_human_review": false,
    "task": {
      "id": "mvp-task-1",
      "description": "Equipment request",
      "priority": "normal",
      "extracted_entities": {
        "equipment": "forklift",
        "location": "bay 4"
      }
    }
  }
}
```

---

## System Health Check

### GET `/mvp/health`

Quick status check of the MVP service.

**Response**:
```json
{
  "status": "healthy",
  "component": "mvp"
}
```

**Example (Monitoring)**:
```bash
# Check every 30 seconds
while true; do
  curl -s http://localhost:8800/mvp/health | jq .
  sleep 30
done
```

---

## Integration Examples

### Voice-to-Dashboard Pipeline

```
Voice Input
    ↓
[Transcription Service] (speech-to-text)
    ↓
POST /mvp/process (text → intent)
    ↓
Generate Task Object
    ↓
POST /mvp/notify (broadcast to dashboard)
    ↓
Dashboard Updates in Real-Time ✓
```

### Multi-Source Task Aggregation

```python
from fastapi import FastAPI
import requests

app = FastAPI()

# Sources: Walkie-talkie, Phone, Email, Web form
@app.post("/sources/walkie-talkie")
def from_walkie(text: str, operator_id: str):
    # Process through intent classifier
    task = create_task(text, "walkie-talkie", operator_id)
    # Broadcast to dashboard
    requests.post("http://localhost:8800/mvp/notify", json=task)
    return {"status": "sent to dashboard"}

@app.post("/sources/voip-phone")
def from_phone(call_data: dict):
    # Convert voice to text
    text = transcribe(call_data['audio'])
    task = create_task(text, "voip-phone", call_data['caller_id'])
    # Broadcast to dashboard
    requests.post("http://localhost:8800/mvp/notify", json=task)
    return {"status": "sent to dashboard"}

def create_task(text: str, source: str, speaker_id: str) -> dict:
    # Call intent classifier
    classification = classify_intent(text)
    return {
        "id": f"task-{uuid.uuid4()}",
        "description": text,
        "intent": classification['intent'],
        "priority": classification['priority'],
        "extracted_entities": classification['entities'],
        "requires_human_review": classification['confidence'] < 0.7,
        "source": source,
        "speaker": speaker_id
    }
```

### Dashboard Event Listener (Node.js Backend)

```javascript
const express = require('express');
const fetch = require('node-fetch');

const app = express();

// Connect to dashboard stream
async function streamTasks() {
    const response = await fetch('http://localhost:8800/mvp/stream');
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const task = JSON.parse(line.slice(6));
                console.log('Dashboard received:', task);
                
                // Route to appropriate handler
                handleTask(task);
            }
        }
    }
}

function handleTask(task) {
    console.log(`[${task.intent}] ${task.description}`);
    console.log(`  Item: ${task.extracted_entities.item}`);
    console.log(`  Location: ${task.extracted_entities.location}`);
    
    if (task.requires_human_review) {
        console.warn(`  ⚠️  Needs human review`);
    }
}

// Start streaming
streamTasks().catch(err => {
    console.error('Stream error:', err);
    setTimeout(streamTasks, 5000); // Reconnect
});
```

---

## Data Schema Reference

### Task Object
```typescript
interface Task {
  id: string;                          // Unique identifier
  description: string;                 // Raw transcription or task text
  intent: "ORDER" | "STATUS_UPDATE" | "EMERGENCY" | "INQUIRY" | "ESCALATION";
  priority: "high" | "normal" | "low";
  extracted_entities: {
    item: string;                      // Equipment/item name
    location: string;                  // Physical location
    [key: string]: unknown;            // Additional fields
  };
  requires_human_review?: boolean;     // Flag for low-confidence tasks
  source?: "walkie-talkie" | "voip-phone" | "web" | "email";
  speaker?: string;                    // Operator/caller ID
  zone?: string;                       // Operational zone
  timestamp?: string;                  // ISO 8601 timestamp
}
```

### Intent Types
- **ORDER**: Request for equipment or resources
- **STATUS_UPDATE**: Information sharing about current state
- **EMERGENCY**: Urgent/critical situation requiring immediate action
- **INQUIRY**: Question or request for information
- **ESCALATION**: Needs management/supervisor approval

### Priority Levels
- **HIGH**: Mission-critical, requires immediate attention
- **NORMAL**: Standard task (default)
- **LOW**: Background task, can be deferred

---

## Error Handling

### Common Errors

**400 Bad Request** - Malformed JSON
```json
{
  "status": "error",
  "error": "Invalid JSON payload"
}
```

**500 Internal Server Error** - Database or processing failure
```json
{
  "status": "error",
  "error": "Failed to persist notification"
}
```

**SSE Connection Lost**
- Browser automatically reconnects
- Messages during disconnect are lost (not replayed)
- Use `/mvp/history` to catch up

### Retry Strategy

```python
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.3)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    return session

session = create_session()
response = session.post('http://localhost:8800/mvp/notify', json=task)
```

---

## Rate Limiting

Currently **unlimited** - suitable for MVP. For production:
- Implement: 100 tasks/second per source
- Queue: High-velocity loads in Redis
- Throttle: Prioritize human-review tasks
- Monitor: Dashboard performance at 1000+ tasks/hour

---

## Authentication (Future)

```python
# Not yet implemented - roadmap for production
@app.post("/mvp/notify")
async def notify_secure(payload: dict, token: str = Header(...)):
    # Verify JWT token
    # Rate-limit by organization
    # Audit log all changes
    pass
```

---

## Performance Tips

1. **Batch notifications** if sending multiple tasks
2. **Use history endpoint** for backfill, not loop polling
3. **Close SSE connection** when tab is not visible
4. **Implement exponential backoff** for retries
5. **Monitor network bandwidth** for high-throughput scenarios

---

## Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test SSE Connection

```bash
# In terminal, watch live stream
curl -N http://localhost:8800/mvp/stream

# In another terminal, send a test task
curl -X POST http://localhost:8800/mvp/notify \
  -H "Content-Type: application/json" \
  -d '{"id":"test-123","description":"Test","intent":"ORDER"...}'
```

### Browser DevTools

1. Open DevTools (F12)
2. Go to **Network** tab
3. Filter for "stream" (SSE connection)
4. Watch for "data:" messages
5. Check **Console** for errors

---

## Support

For questions or issues:
1. Check `MISSION_CONTROL_GUIDE.md` for user documentation
2. Review this API reference
3. Check browser console for client-side errors
4. Run health check: `GET /mvp/health`
5. Test with curl examples above

---

**API Version**: 1.0  
**Last Updated**: February 2026  
**Status**: Stable MVP
