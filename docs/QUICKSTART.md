# Quick Start Guide

Get the AI Communication Engine running in 5 minutes!

## Prerequisites

- Python 3.12 or higher
- 2 GB RAM minimum
- Internet connection (for API calls)
- Git (optional, for cloning)

## Step 1: Clone or Download (1 min)

```bash
# Option A: Clone from repository
git clone https://github.com/yourname/ai-communication-engine.git
cd ai-communication-engine

# Option B: Download as ZIP and extract
cd "d:\AI Communication Engine"
```

## Step 2: Create Virtual Environment (1 min)

```bash
# Create venv
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.\venv\Scripts\activate.bat

# Activate (macOS/Linux)
source venv/bin/activate
```

**Verify activation**: You should see `(venv)` prompt prefix.

## Step 3: Install Dependencies (2 min)

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; import sqlalchemy; print('✓ All dependencies installed')"
```

## Step 4: Configure (30 seconds)

```bash
# Copy example environment
cp .env.example .env

# For local testing, you can leave defaults:
#   - Uses SQLite (no setup needed)
#   - Intent classification works without API key (rule-based)
#   - Other services need real API keys to function
```

**To enable full features** (optional):

```bash
# Edit .env and add your API keys
notepad .env  # Windows
# or
nano .env     # macOS/Linux

# Required for audio transcription:
OPENAI_API_KEY=sk-...your-key...

# Required for SMS notifications:
TWILIO_ACCOUNT_SID=AC...your-sid...
TWILIO_AUTH_TOKEN=...your-token...

# Required for push notifications:
FIREBASE_CREDENTIALS_PATH=/path/to/service-account.json
```

## Step 5: Run Application (30 seconds)

```bash
# Option A: Using Uvicorn (recommended)
uvicorn AI-CommunicationEngine:app --reload --host 0.0.0.0 --port 8000

# Option B: Direct Python
python AI-CommunicationEngine.py
```

**Success indicators**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Step 6: Test the Service

### A. Health Check (Terminal)
```bash
curl http://localhost:8000/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "service": "AI Communication Engine",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### B. Try the Demo
```bash
# In a new terminal (keep server running)
python demo.py
```

**Demo runs 6 demonstrations**:
1. ✓ Transcription service
2. ✓ Intent classification
3. ✓ Priority calculation
4. ✓ Database operations
5. ✓ Knowledge base queries
6. ✓ Complete workflow

### C. API Documentation
Open in browser: `http://localhost:8000/docs`

(Interactive Swagger UI with all endpoints)

### D. Test REST API
```bash
# Submit transcription for processing
curl -X POST http://localhost:8000/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "caller_id": "ext_123",
    "source": "VOIP_PHONE",
    "audio_data": "..."
  }'

# Get task
curl http://localhost:8000/tasks/task_id_here

# Update task status
curl -X PUT http://localhost:8000/tasks/task_id_here/status \
  -H "Content-Type: application/json" \
  -d '{"new_status": "completed"}'
```

## What Works Out of the Box

✅ **Without API Keys** (Rule-based):
- Intent classification (TASK, INQUIRY, etc.)
- Entity extraction (rooms, quantities, urgency)
- Priority calculation
- Task creation and assignment
- Database storage
- WebSocket endpoints

❌ **Requires API Keys**:
- Transcription (needs OpenAI key)
- SMS notifications (needs Twilio)
- Push notifications (needs Firebase)
- Voice notifications (needs Twilio)

## Using with Audio

### From Python

```python
import asyncio
from models import AudioSource
from AI_CommunicationEngine import middleware, Session

async def test_transcription():
    # Load audio file
    with open("sample_audio.wav", "rb") as f:
        audio_data = f.read()
    
    db = Session()
    result = await middleware.process_audio_stream(
        caller_id="ext_123",
        audio_data=audio_data,
        source=AudioSource.VOIP_PHONE,
        db_session=db
    )
    print(f"Task created: {result['task_id']}")
    db.close()

asyncio.run(test_transcription())
```

### From JavaScript/WebSocket

```javascript
const socket = new WebSocket('ws://localhost:8000/ws/audio/ext_123');

socket.onopen = () => {
  // Send audio chunk
  fetch('sample_audio.wav')
    .then(r => r.arrayBuffer())
    .then(buffer => socket.send(buffer));
};

socket.onmessage = (event) => {
  const result = JSON.parse(event.data);
  console.log('Processing:', result);
};
```

### Using WebSocket with curl
```bash
# Note: websocat command (if installed)
websocat ws://localhost:8000/ws/audio/ext_123 < audio.wav
```

## Using Webhooks

### Twilio Setup

1. Go to Twilio Console → Phone Numbers → Manage
2. Set Voice Webhook: `https://yourdomain.com/webhooks/twilio`
3. Set SMS Webhook: `https://yourdomain.com/webhooks/twilio`

**For local testing with ngrok**:
```bash
# Terminal 1: Start ngrok
ngrok http 8000
# Copy forwarding URL: https://abc123.ngrok.io

# Terminal 2: Update Twilio webhooks to:
# https://abc123.ngrok.io/webhooks/twilio
```

### Vonage Setup

1. Create Vonage account
2. Set webhook to: `https://yourdomain.com/webhooks/vonage`

## Database

### View Data

```bash
# SQLite CLI
sqlite3 communication_engine.db

# SQL queries
sqlite> SELECT COUNT(*) FROM task;
sqlite> SELECT * FROM transcription LIMIT 5;
sqlite> SELECT * FROM staff_member;
```

### Reset Database

```bash
# Delete all tables
rm communication_engine.db

# Recreate on next run
# (Auto-created when app starts)
```

### Backup

```bash
# Create backup
cp communication_engine.db communication_engine.db.backup

# Restore
cp communication_engine.db.backup communication_engine.db
```

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"
```bash
# Solution: Use different port
uvicorn AI-CommunicationEngine:app --port 8001

# Or kill existing process
lsof -Ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows
```

### Issue: "OPENAI_API_KEY not found"
```bash
# Solution: Set in .env or environment
export OPENAI_API_KEY='sk-...'

# Or use without transcription (rule-based only)
```

### Issue: "Database locked" (SQLite)
```bash
# Solution: Restart service and check for locks
rm -f communication_engine.db-*
```

### Issue: PowerShell execution policy
```bash
# Solution: Allow script execution (one-time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Next Steps

### 1. Explore Features
- Review [README.md](README.md) for complete documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Read code comments in each module

### 2. Configure for Production
- Set up PostgreSQL (instead of SQLite)
- Add Redis for caching/sessions
- Enable HTTPS/SSL
- Set up logging aggregation
- Configure monitoring

### 3. Integrate with Your System
- Register webhooks from VoIP/radio systems
- Configure staff member profiles
- Set up inventory items
- Create knowledge base entries
- Configure email/SMS attributes

### 4. Customize
- Add custom intent types
- Extend entity extraction
- Create domain-specific rules
- Add more knowledge base entries
- Custom notification channels

### 5. Deploy
- See [Deployment Options](README.md#deployment)
- Use Docker for consistency
- Deploy to cloud (AWS, Google Cloud, Azure)
- Set up CI/CD pipeline

## Key Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/transcribe` | Process audio |
| GET | `/tasks/{id}` | Get task details |
| PUT | `/tasks/{id}/status` | Update task status |
| GET | `/streams` | List active streams |
| POST | `/webhooks/twilio` | Twilio webhook |
| POST | `/webhooks/vonage` | Vonage webhook |
| WS | `/ws/audio/{id}` | WebSocket streaming |

## Performance Tips

**To handle more concurrent streams**:
```python
# In AI-CommunicationEngine.py
AudioStreamManager(max_streams=100)  # Increase from 50
```

**To optimize database**:
```bash
# Use PostgreSQL instead of SQLite
# Update config.ini:
# url = postgresql://user:pass@localhost/engine
```

**To speed up transcription**:
```bash
# Use local Whisper model (no internet needed)
# Install: pip install openai-whisper
# Use: TranscriptionProvider.LOCAL
```

## Support Resources

- **Documentation**: [README.md](README.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Docs**: `http://localhost:8000/docs`
- **Issues**: Check GitHub Issues
- **Email**: support@example.com

## Success Criteria

After completing this guide, you should be able to:

✅ Start the AI Communication Engine
✅ Access the health check endpoint
✅ Submit audio for processing  
✅ View created tasks in database
✅ Understand the data pipeline
✅ Run the demo script successfully
✅ Access API documentation

## You're Ready!

The AI Communication Engine is now running. Explore the documentation and APIs to integrate it with your systems.

**Questions?** Check the full [README.md](README.md) or review [ARCHITECTURE.md](ARCHITECTURE.md) for detailed information.

Happy building! 🚀
