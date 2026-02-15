# Project Structure

## Overview
The AI Communication Engine project is organized into logical folders for better maintainability and clarity.

## Directory Layout

```
ai-communication-engine/
├── README.md                      # Main project documentation
├── setup.py                       # Python package setup configuration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
│
├── src/                          # Core application source code
│   ├── __init__.py
│   ├── AI-CommunicationEngine.py  # Main application entry point
│   ├── intent_classifier.py       # Intent classification and extraction
│   ├── models.py                  # Database models (SQLAlchemy)
│   ├── notification_service.py    # Notification management
│   ├── task_action_engine.py      # Task processing and assignment
│   ├── transcription_service.py   # Speech-to-text transcription
│   └── webhook_handlers.py        # VoIP/walkie-talkie webhook handlers
│
├── mvp/                          # Mission Control Dashboard MVP
│   ├── app.py                     # FastAPI backend server (port 8800)
│   ├── Dockerfile                 # MVP Docker container
│   ├── requirements.txt           # MVP-specific dependencies
│   ├── README.md                  # MVP documentation
│   ├── demo.py                    # Demo/test scripts
│   ├── static/
│   │   └── index.html             # Static assets
│   └── templates/
│       ├── base.html              # Base HTML template
│       ├── catch.html             # Catch-all route template
│       └── index.html             # React dashboard UI (JSX)
│
├── tests/                        # Test suite
│   ├── test_integration.py        # Integration tests
│   ├── test_dashboard.py          # Dashboard endpoint tests
│   ├── test_root.py               # Root endpoint tests
│   └── test_quick.ps1             # PowerShell quick test script
│
├── docker/                       # Docker configuration
│   ├── Dockerfile                 # Main application Docker image
│   ├── docker-compose.yml         # Multi-service Docker Compose
│   └── docker-compose.mvp.yml     # MVP-only Docker Compose
│
├── config/                       # Configuration files
│   └── config.ini                 # Application configuration
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md            # System architecture
│   ├── API_REFERENCE.md           # API endpoint documentation
│   ├── MISSION_CONTROL_GUIDE.md   # Dashboard user guide
│   ├── TECHNICAL_IMPLEMENTATION.md # Implementation details
│   ├── RUNNING_AND_TESTING.md     # How to run and test
│   ├── QUICK_REFERENCE.md         # Quick start guide
│   ├── QUICKSTART.md              # Getting started
│   └── STATUS.md                  # Project status
│
├── scripts/                      # Utility scripts
│   └── fix_jsx.py                 # JSX format fixer
│
└── venv/                         # Python virtual environment
```

## Quick References

### Running the Application

**MVP Dashboard (FastAPI + React):**
```bash
cd mvp
python -m uvicorn app:app --host 127.0.0.1 --port 8800 --reload
# Access at http://127.0.0.1:8800/
```

**Main Application:**
```bash
python src/AI-CommunicationEngine.py
```

### Running Tests

```bash
# Python integration tests
python -m pytest tests/test_integration.py -v

# Dashboard endpoint tests
python tests/test_dashboard.py

# Quick PowerShell test
.\tests\test_quick.ps1
```

### Docker Deployment

```bash
# MVP only
docker-compose -f docker/docker-compose.mvp.yml up

# Full stack
docker-compose -f docker/docker-compose.yml up
```

## Module Import Paths

After reorganization, import statements should use the following format:

```python
# From core modules in src/
from src.intent_classifier import IntentClassifier
from src.models import Task, Session
from src.notification_service import NotificationService
from src.task_action_engine import TaskActionEngine
from src.transcription_service import TranscriptionService
from src.webhook_handlers import TwilioWebhookHandler

# From MVP
from mvp.app import app
```

## Configuration

- **Main config:** `config/config.ini`
- **Environment variables:** `.env.example` → `.env`
- **Database location:** `.` (SQLite in root by default)

## Folder Responsibilities

| Folder | Purpose |
|--------|---------|
| `src/` | Core business logic and services |
| `mvp/` | Real-time dispatch dashboard (React + FastAPI) |
| `tests/` | Automated test suite |
| `docker/` | Container configurations |
| `config/` | Application configuration files |
| `docs/` | Project documentation |
| `scripts/` | Utility and maintenance scripts |

---

**Last Updated:** February 14, 2026
