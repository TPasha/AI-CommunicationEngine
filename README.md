# AI Communication Engine

**Real-time Intelligence Middleware for VoIP & Walkie-Talkie Systems**

A sophisticated Python middleware that processes audio from VoIP and walkie-talkie sources, transcribes conversations, classifies intent, automatically creates prioritized tasks, and sends intelligent notifications to relevant staff—all in real-time.

## Features

✨ **Core Capabilities**
- 🎤 **Multi-source Audio Input**: VoIP calls, SMS messages, walkie-talkie transmissions
- 🗣️ **Real-time Transcription**: OpenAI Whisper with 11+ language support
- 🧠 **AI Intent Classification**: GPT-4 Turbo with rule-based fallback
- 📊 **Intelligent Prioritization**: Multi-factor priority calculation engine
- 👥 **Smart Staff Assignment**: Skill-based, availability-aware task distribution
- 🔔 **Multi-channel Notifications**: Push, SMS, Email, Voice alerts
- 🗄️ **Persistent Storage**: SQLAlchemy ORM with relational database
- ⚡ **High Performance**: Async/await architecture, concurrent stream handling
- 🔐 **Webhook Security**: Signature validation for Twilio, Vonage, custom systems
- 💾 **Entity Extraction**: Regex-based extraction of rooms, quantities, urgency levels

## Quick Start

### 1. Prerequisites

```bash
# Python 3.12+ required
python --version  # Must be 3.12.0 or higher

# Clone or download project
cd "d:\AI Communication Engine"
```

### 2. Virtual Environment Setup

The virtual environment is stored outside the project at `d:\venv_aice` for better organization.

```bash
# Activate (Windows PowerShell)
& "d:\venv_aice\Scripts\Activate.ps1"

# Activate (Command Prompt)
d:\venv_aice\Scripts\activate.bat

# Activate (macOS/Linux)
source /path/to/venv_aice/bin/activate
```

Or use the venv Python executable directly:
```bash
d:\venv_aice\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# - OPENAI_API_KEY
# - TWILIO_ACCOUNT_SID / AUTH_TOKEN
# - VONAGE_API_KEY / API_SECRET
# - FIREBASE_CREDENTIALS_PATH (for push notifications)
```

### 5. Initialize Database

```bash
# Database auto-initializes on first run
python -c "from src.models import init_db; init_db()"
```

### 6. Run the Service

#### Option A: Using Uvicorn (Recommended - Main Engine)
```bash
uvicorn src.AI-CommunicationEngine:app --reload --host 0.0.0.0 --port 8000
```

#### Option B: Web Dashboard (MVP)
```bash
uvicorn src.web_app:app --reload --host 127.0.0.1 --port 8800
```

#### Option C: Direct Python
```bash
python src/AI-CommunicationEngine.py
```

### 7. Test the Service

```bash
# Run integration tests
pytest tests/test_integration.py -v

# Run Hugging Face integration tests
pytest tests/test_huggingface_integration.py -v

# Run all tests
pytest tests/ -v

# Check health endpoint
curl http://localhost:8000/health
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    External Sources                         │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │  Twilio  │  │ Vonage   │  │ Walkie   │  │  WebSock │   │
│   │  VoIP    │  │   SMS    │  │ Talkie   │  │   et     │   │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└────────┼─────────────┼─────────────┼─────────────┼──────────┘
         │             │             │             │
         └──────────────┴─────────────┴─────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │   Webhook Router &          │
         │   Signature Validation      │
         └────────────┬────────────────┘
                      │
                      ▼
         ┌─────────────────────────────┐
         │  Transcription Service      │
         │  (OpenAI Whisper/Others)    │
         └────────────┬────────────────┘
                      │
                      ▼
         ┌─────────────────────────────┐
         │  Intent Classifier          │
         │  (GPT-4 + Rule-based)       │
         └────────────┬────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
    ┌────────────┐         ┌──────────────┐
    │   TASK     │         │  INQUIRY     │
    │   ENGINE   │         │  RESPONSE    │
    └────┬───────┘         └──────────────┘
         │
    ┌────┴──────────────┬─────────────────┐
    │                   │                 │
    ▼                   ▼                 ▼
┌────────────┐  ┌───────────────┐  ┌────────────┐
│Prioritizer │  │Task Assigner  │  │PMS Sync    │
└────┬───────┘  └───────┬───────┘  └────────────┘
     │                  │
     └──────────┬───────┘
                │
                ▼
    ┌──────────────────────────────┐
    │  Notification Service        │
    │  (Push/SMS/Email/Voice)      │
    └──────────────────────────────┘
                │
    ┌───────────┼───────────┬──────────────┐
    │           │           │              │
    ▼           ▼           ▼              ▼
  Push        SMS        Email          Voice
  (FCM)    (Twilio)   (SMTP)      (Twilio TTS)

    Database (SQLAlchemy ORM)
    - Transcriptions
    - Tasks & Updates
    - Staff Members
    - Availability Status
    - Inventory Status
    - Audio Sessions
```

## API Endpoints

### Health Check
```http
GET /health
```

### Transcribe Audio
```http
POST /transcribe
Content-Type: application/json

{
  "caller_id": "ext_123",
  "source": "VOIP_PHONE|WALKIE_TALKIE|DIRECT_CALL",
  "audio_data": "<base64-encoded-audio>",
  "speaker_name": "John Smith"
}

Response:
{
  "transcription_id": "txn_abc123",
  "text": "Room 301 needs towels",
  "confidence": 0.95,
  "intent_type": "TASK",
  "priority": 4,
  "assigned_to": "staff_id_123",
  "location": "Room 301"
}
```

### Twilio Webhook
```http
POST /webhooks/twilio
```

### Vonage Webhook
```http
POST /webhooks/vonage
```

### Walkie-Talkie Webhook
```http
POST /webhooks/walkie-talkie
```

### Get Active Streams
```http
GET /streams

Response:
{
  "active_streams": 12,
  "max_streams": 50,
  "current": [...]
}
```

### Get Task
```http
GET /tasks/{task_id}

Response:
{
  "id": "task_123",
  "description": "Deliver towels to room 301",
  "priority": 4,
  "status": "pending",
  "location": "Room 301",
  "assigned_to": "staff_123",
  "created_at": "2024-01-15T10:30:00",
  "due_date": "2024-01-15T11:00:00"
}
```

### Update Task Status
```http
PUT /tasks/{task_id}/status
Content-Type: application/json

{
  "new_status": "completed"
}
```

### WebSocket Real-time Streaming
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/audio/caller_123');

// Send audio chunks
ws.send(audioChunk);

// Receive acknowledgements
ws.onmessage = (event) => {
  console.log(JSON.parse(event.data));
};
```

## Database Schema

### Core Tables

**Transcription**
- `id`: UUID primary key
- `source`: AudioSource enum (VOIP_PHONE, WALKIE_TALKIE, DIRECT_CALL)
- `raw_text`: Transcribed text
- `confidence_score`: 0-1 confidence
- `speaker_id`: Caller/device identifier
- `intent_type`: IntentType enum
- `requires_human_review`: Boolean flag
- `processing_timestamp`: Created at

**Task**
- `id`: UUID primary key
- `transcription_id`: Foreign key to Transcription
- `description`: Task description
- `priority`: 1-5 scale
- `status`: TaskStatus enum (PENDING, IN_PROGRESS, COMPLETED, etc.)
- `location`: Room/area identifier
- `item_required`: Item to fetch/repair
- `quantity`: Quantity needed
- `assigned_to`: Foreign key to StaffMember
- `created_at`, `due_date`, `completed_at`: Timestamps

**StaffMember**
- `id`: UUID primary key
- `name`: Staff name
- `role`: Job title
- `department`: Department name
- `phone_number`: Contact number
- `email`: Email address
- `device_token`: Firebase Cloud Messaging token
- `availability_status`: StaffAvailabilityStatus enum
- `skills`: Comma-separated skill list
- `notification_preferences`: JSON preferences

**InventoryStatus**
- `id`: UUID primary key
- `item_name`: Item identifier
- `category`: Category (towels, toiletries, etc.)
- `quantity_available`: Current quantity
- `quantity_total`: Total capacity
- `in_stock`: Boolean
- `needs_reorder`: Boolean flag

## Configuration

Edit `config.ini`:

```ini
[database]
url = sqlite:///communication_engine.db  # or postgresql://...

[transcription]
provider = openai_whisper
model = whisper-1

[llm]
provider = openai
model = gpt-4-turbo-preview
temperature = 0.7

[websocket]
host = 0.0.0.0
port = 8000

[twilio]
account_sid = your_sid_here
auth_token = your_token_here
phone_number = +1234567890
webhook_url = https://yourdomain.com/webhooks/twilio

[vonage]
api_key = your_key
api_secret = your_secret

[firebase]
credentials_path = /path/to/serviceAccountKey.json

[performance]
max_concurrent_streams = 50
timeout_ms = 30000
```

## Usage Examples

### Python Client

```python
import asyncio
from src.models import init_db, AudioSource, IntentType
from AI_CommunicationEngine import middleware

async def process_call(audio_bytes):
    result = await middleware.process_audio_stream(
        caller_id="ext_123",
        audio_data=audio_bytes,
        source=AudioSource.VOIP_PHONE,
        db_session=db
    )
    print(f"Task created: {result['task_id']}")
    print(f"Priority: {result['priority']}/5")

asyncio.run(process_call(audio_data))
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Submit audio for processing
curl -X POST http://localhost:8000/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "caller_id": "ext_205",
    "source": "VOIP_PHONE",
    "audio_data": "base64_encoded_audio"
  }'

# Get task details
curl http://localhost:8000/tasks/task_abc123

# Update task status
curl -X PUT http://localhost:8000/tasks/task_abc123/status \
  -H "Content-Type: application/json" \
  -d '{"new_status": "completed"}'
```

### JavaScript/Node.js

```javascript
// WebSocket streaming
const socket = new WebSocket('ws://localhost:8000/ws/audio/ext_123');

socket.addEventListener('open', () => {
  console.log('Connected to AI Engine');
  // Send audio chunks
  socket.send(audioChunk1);
  socket.send(audioChunk2);
});

socket.addEventListener('message', (event) => {
  const response = JSON.parse(event.data);
  console.log('Chunk received:', response);
});

// REST API
async function submitAudio(audioData) {
  const response = await fetch('http://localhost:8000/transcribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      caller_id: 'ext_123',
      source: 'VOIP_PHONE',
      audio_data: audioData
    })
  });
  return response.json();
}
```

## Testing

```bash
# Run all tests
pytest tests/test_integration.py -v

# Run specific test class
pytest tests/test_integration.py::TestDatabaseModels -v

# Run with coverage
pytest tests/test_integration.py --cov=.

# Run demo
python mvp/demo.py
```

## Performance

- **Transcription**: ~2-5 seconds for 1-minute audio
- **Intent Classification**: ~500ms with LLM, instant with rules
- **Database Operations**: <100ms for typical queries
- **Concurrent Streams**: 50+ simultaneous audio streams
- **Notification Delivery**: <1 second average latency
- **Priority Calculation**: <50ms

## Troubleshooting

### ImportError: No module named 'openai'
```bash
pip install -r requirements.txt
```

### Database locked error
```bash
# Remove old lock files if using SQLite
rm communication_engine.db communication_engine.db-*
```

### API Key errors
```bash
# Verify your .env file
cat .env

# Check OpenAI API key validity
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Webhook signature validation fails
- Ensure auth tokens in .env match provider settings
- Check request body is unmodified between transmission and validation
- Verify webhook URL is HTTPS with valid certificate

## Deployment

### Docker

```bash
cd docker
docker build -t ai-comm-engine:latest -f Dockerfile ..
docker run -p 8000:8000 --env-file .env ai-comm-engine:latest
```

### Docker Compose

```bash
cd docker
docker-compose up -d
```

### Cloud Platforms

**AWS Lambda**: See `serverless.yml`
**Google Cloud Run**: See `cloudbuild.yaml`
**Azure Functions**: See `function_app.py`

## Development

```bash
# Code formatting
black .

# Linting
flake8 .

# Type checking
mypy .

# Pre-commit hooks
pre-commit install
```

## API Documentation

Once running, visit: `http://localhost:8000/docs` (Swagger UI)

## License

MIT License - See LICENSE file

## Support

- 📧 Email: support@example.com
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

## Changelog

### Version 1.0.0 (2024-01-15)
- ✅ Initial release
- ✅ Multi-source audio input support
- ✅ Real-time transcription with Whisper
- ✅ Intent classification with GPT-4 Turbo
- ✅ Task prioritization and assignment
- ✅ Multi-channel notifications
- ✅ Webhook handlers for Twilio/Vonage

---

**Built with ❤️ for real-time communication intelligence**
