# AI Communication Engine — MVP

This folder contains a minimal Proof-of-Concept FastAPI app that demonstrates the core intent classification + simple task creation flow.

Quick start

1. Create and activate a Python virtualenv (recommended).
2. Install dependencies:

```bash
pip install -r mvp/requirements.txt
```

3. Run the app:

```bash
uvicorn mvp.app:app --reload --port 8800
```

4. Example request:

```bash
curl -X POST http://127.0.0.1:8800/mvp/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Room 302 needs towels immediately", "speaker_id": "caller-1"}'
```

Output will include a classification object and a simple `task` entry when applicable.

Files

- `app.py` — FastAPI MVP endpoints using the repo's `intent_classifier`.
- `requirements.txt` — minimal dependencies for running the MVP.

Docker demo

Build and run the MVP in Docker (recommended for a demo):

```bash
# from project root
docker compose -f docker-compose.mvp.yml up --build -d
```

Then open the UI at: http://localhost:8830/mvp/ui

