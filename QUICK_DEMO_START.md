# 🚀 Quick Demo Start Guide

## ⚡ 3-Step Demo Setup

### Step 1: Create .env File (30 seconds)
```powershell
cd "d:\AI Communication Engine"
Copy-Item .env.example .env
notepad .env
```

**Minimal config (add to .env)**:
```ini
TRANSCRIPTION_PROVIDER=huggingface_whisper
LLM_PROVIDER=huggingface
DATABASE_URL=sqlite:///communication_engine.db
```

### Step 2: Start Server (10 seconds)
```powershell
uvicorn src.web_app:app --host 127.0.0.1 --port 8800
```

### Step 3: Open Dashboard
**URL**: http://127.0.0.1:8800

---

## 🎤 Demo Script (2 minutes)

### What to say to your audience:

**1. Introduction (15 seconds)**
> "This is an AI-powered communication hub that processes voice commands in real-time, transcribes them, classifies intent, and creates prioritized tasks automatically."

**2. Show Auto-Generated Tasks (15 seconds)**
- Point to left panel: "The Wire shows raw transcriptions"
- Point to right panel: "The Queue shows processed tasks with priorities"
- Highlight: Orange cards = needs human review, Red = urgent

**3. Voice Demo (60 seconds)**
- Click green 🎤 mic button
- Say: **"Emergency - send forklift to Loading Dock immediately"**
- Click red stop button
- Show transcription appearing in left panel
- Show task card with HIGH priority and extracted data
- Click "REVIEW" button to show confidence score

**4. Features Highlight (30 seconds)**
- Real-time SSE stream (no polling)
- Automatic entity extraction (items, locations)
- Confidence-based human review queue
- Multi-source input (voice, VoIP, walkie-talkie)
- Elapsed time tracking per task

---

## ✅ What Works Right Now

✅ Voice recording from browser  
✅ Real-time transcription (HuggingFace Whisper)  
✅ Intent classification (rule-based fallback)  
✅ Task prioritization  
✅ SSE streaming updates  
✅ Mock task generation  
✅ Review queue for low-confidence items  
✅ Responsive UI with animations  

---

## 🎯 Key Demo Talking Points

1. **Zero-latency Processing**: Tasks appear as you speak
2. **Human-in-the-Loop**: Low confidence items flagged for review
3. **Context Aware**: Extracts items, locations, urgency automatically
4. **Multi-channel**: Can integrate VoIP, SMS, walkie-talkies
5. **Production Ready**: Built on FastAPI, async/await, SQLAlchemy

---

## 🐛 If Something Goes Wrong

### Mic doesn't work?
- Use mock tasks (auto-generate every 3 seconds)
- Say: "We're seeing simulated live data here"

### Server won't start?
```powershell
# Try a different port
uvicorn src.web_app:app --port 8801
```

### Slow first transcription?
- Expected! HuggingFace loads model first time
- Say: "First transcription loads the AI model - subsequent ones are instant"

---

## 📱 Backup Plan

If all else fails, show the code:
1. Open `web/templates/index.html` - Show React components
2. Open `src/web_app.py` - Show FastAPI endpoints
3. Open `src/transcription_service.py` - Show Whisper integration

---

## 🎬 Sample Voice Commands

1. "Send maintenance to room 305 ASAP"
2. "Requesting two towels for Bay 2"  
3. "Emergency - forklift needed at Loading Dock"
4. "Status update - inventory complete in Zone A"
5. "Need six coffee pods delivered to room 412"

---

**Pro Tip**: Keep browser DevTools open (F12) > Network tab to show live SSE stream connection!
