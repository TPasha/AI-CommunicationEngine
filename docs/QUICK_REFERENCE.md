# 🎯 AI COMMAND CENTER - QUICK START CARD

## ✅ SERVER STATUS: RUNNING

```
┌─────────────────────────────────────────────┐
│  Dashboard URL: http://127.0.0.1:8800       │
│  Health API:   http://127.0.0.1:8800/health │
│  Port:         8800                         │
│  Framework:    FastAPI + Uvicorn            │
│  Status:       🟢 LIVE                      │
└─────────────────────────────────────────────┘
```

---

## 🎮 TESTING

### 1. View Dashboard
```
Open: http://127.0.0.1:8800
✅ Should see Mission Control interface
✅ Header with System Pulse waveform
✅ "The Wire" feed (left)
✅ "The Queue" cards (right)
```

### 2. Send Test Task
```bash
curl -X POST http://127.0.0.1:8800/mvp/notify \
  -H "Content-Type: application/json" \
  -d '{
    "id":"test-1",
    "description":"Requesting Forklift B for Bay 4",
    "intent":"ORDER",
    "priority":"high",
    "extracted_entities":{"item":"Forklift B","location":"Bay 4"},
    "requires_human_review":false
  }'
```
✅ Task appears INSTANTLY in dashboard

### 3. Check Health
```bash
curl http://127.0.0.1:8800/mvp/health
# Returns: {"status":"healthy","component":"mvp"}
```

### 4. Get Task History
```bash
curl http://127.0.0.1:8800/mvp/history?limit=5
# Returns: JSON array of stored tasks
```

---

## 🎨 VISUAL INDICATORS

| What You See | What It Means | Action |
|---|---|---|
| **Red Glow** | High Priority | Immediate attention needed |
| **Blue Glow** | Normal Priority | Standard processing |
| **Orange Pulsing** | Review Required | Click [REVIEW] button |
| **Cyan Waveform** | Transmitting | Audio/voice received |
| **Count Timer** | Time Pending | Older tasks are more urgent |

---

## 📡 LIVE UPDATE TEST

### Watch Real-Time Magic:
1. Open dashboard in browser
2. In terminal, run curl command (see above)
3. **INSTANTLY** see task appear in "The Queue"
4. Watch countdown timer auto-increment

---

## 🚀 COMMON TASKS

### Send High-Priority Emergency
```bash
curl -X POST http://127.0.0.1:8800/mvp/notify \
  -H "Content-Type: application/json" \
  -d '{"id":"emerg-1","description":"Equipment failure!","intent":"EMERGENCY","priority":"high","extracted_entities":{"item":"Forklift","location":"BAY 1"},"requires_human_review":false}'
```
➜ Appears with RED GLOW at top

### Send Review-Required Task
```bash
curl -X POST http://127.0.0.1:8800/mvp/notify \
  -H "Content-Type: application/json" \
  -d '{"id":"review-1","description":"Unclear status","intent":"INQUIRY","priority":"normal","extracted_entities":{"item":"Status","location":"Zone A"},"requires_human_review":true}'
```
➜ Appears with ORANGE PULSING at top

### Get Last 20 Tasks
```bash
curl http://127.0.0.1:8800/mvp/history?limit=20
```

---

## 📚 DOCUMENTATION

| Document | Purpose |
|---|---|
| **MISSION_CONTROL_GUIDE.md** | User guide, design system, workflows |
| **API_REFERENCE.md** | Complete API docs with examples |
| **TECHNICAL_IMPLEMENTATION.md** | Code structure, component details |
| **RUNNING_AND_TESTING.md** | This detailed testing guide |

---

## ⚙️ MANAGEMENT

### Restart Server
```bash
# Kill and restart
pkill -f uvicorn
cd "d:\AI Communication Engine"
python -m uvicorn mvp.app:app --host 127.0.0.1 --port 8800
```

### Change Port
```bash
python -m uvicorn mvp.app:app --host 127.0.0.1 --port 9000
# Then access at: http://127.0.0.1:9000
```

### Monitor Logs
Check terminal where server is running for:
- Request logs: `127.0.0.1 - "GET / HTTP/1.1" 200`
- SSE connections: `Connected to /mvp/stream`
- Task broadcasts: Task published to N subscribers

---

## ✨ FEATURE CHECKLIST

- ✅ Real-time dashboard
- ✅ Server-Sent Events (no polling)
- ✅ Task persistence (SQLite)
- ✅ Priority-based sorting
- ✅ Confidence-based review flagging
- ✅ Auto-updating countdowns
- ✅ Color-coded intent badges
- ✅ Animated waveforms
- ✅ Mobile responsive (future)
- ✅ Zero-latency updates

---

## 🎯 NEXT INTEGRATION

```python
# From your IntentClassifier:
classification = await classifier.classify(text, speaker_id)

# Create task:
task = {
    "id": f"task-{uuid.uuid4()}",
    "description": classification.primary_intent,
    "intent": classification.intent_type.value,
    "priority": classification.suggested_priority,
    "extracted_entities": classification.extracted_entities,
    "requires_human_review": classification.confidence_score < 0.70
}

# Send to dashboard:
import requests
requests.post("http://127.0.0.1:8800/mvp/notify", json=task)

# ✅ Dashboard updates automatically via SSE
```

---

## 🔍 TROUBLESHOOTING

| Problem | Solution |
|---|---|
| Dashboard blank | Hard refresh (Ctrl+Shift+R) or check console |
| No updates | Verify `/mvp/stream` in Network tab |
| Port in use | Change port or kill process on 8800 |
| Server crash | Check ERROR in terminal, restart |
| Tasks disappeared | Refresh page, check `/mvp/history` |

---

## 📞 ENDPOINTS SUMMARY

```
GET  /                    Dashboard
GET  /mvp                 Dashboard (alias)
GET  /mvp/ui              Dashboard (alias)
GET  /mvp/health          Health check
GET  /mvp/history         Task history
GET  /mvp/stream          Real-time events (SSE)
POST /mvp/notify          Publish task
```

---

**Everything is ready!** 🚀

Open **http://127.0.0.1:8800** and start sending tasks!
