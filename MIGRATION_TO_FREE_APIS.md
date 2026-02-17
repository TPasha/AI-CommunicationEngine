# 🆓 Migration Guide: Moving to Free/Local APIs

## Executive Summary

This document provides a comprehensive plan to eliminate or minimize paid API costs in the AI Communication Engine project.

---

## 📊 Current Status Assessment

### ✅ Already Free (No Action Needed)

| Service | Status | Provider | Why It's Free |
|---------|--------|----------|---------------|
| **Speech Recognition** | ✅ FREE | Hugging Face Transformers | Open-source models (Whisper) |
| **Intent Classification** | ✅ FREE | Hugging Face Transformers | Open-source models (BART) |
| **Database** | ✅ FREE | SQLite | Local file-based database |
| **Web Framework** | ✅ FREE | FastAPI | Open-source Python library |

### 💰 Currently Paid (Need Alternatives)

| Service | Current Cost | Monthly Est. | Usage |
|---------|--------------|--------------|-------|
| **Twilio Voice** | $0.013/minute | $50-200 | VoIP calls |
| **Twilio SMS** | $0.0079/message | $10-50 | Text messages |
| **Vonage (Alternative)** | Similar to Twilio | $50-200 | Backup provider |
| **Firebase Push** | FREE tier available | $0-10 | Notifications |

**Total Estimated Monthly Cost: $110-460**

---

## 🎯 Migration Strategy

### **Option 1: Keep Minimal Paid Services (Recommended)**

**Cost: $0-25/month**

✅ **What to Keep:**
- Firebase Cloud Messaging (FCM) - FREE tier (unlimited messages)
- Twilio FREE trial credits for testing

🔄 **What to Replace:**
- Twilio Voice → Asterisk + SIP
- Twilio SMS → Textbelt API (Free tier)

---

### **Option 2: Fully Free/Local (Advanced)**

**Cost: $0/month**

Replace everything with self-hosted solutions.

---

## 🔧 Detailed Migration Plans

---

## 1️⃣ Voice Calls: Twilio → Asterisk PBX

### **What is Asterisk?**
Asterisk is a FREE, open-source phone system (PBX) that you install on your own server.

### **Benefits:**
- ✅ 100% Free (no per-minute charges)
- ✅ Full control over call routing
- ✅ No vendor lock-in
- ✅ Supports SIP, WebRTC, PSTN

### **Requirements:**
- Server (can be local PC or cloud VM)
- SIP trunk provider (optional, for real phone numbers)
- Basic Linux knowledge

### **Implementation Steps:**

#### Step 1: Install Asterisk
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install asterisk asterisk-core-sounds-en

# Start Asterisk
sudo systemctl start asterisk
sudo systemctl enable asterisk
```

#### Step 2: Configure SIP Endpoint
Edit `/etc/asterisk/pjsip.conf`:
```ini
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

[walkietalkie]
type=endpoint
context=incoming
disallow=all
allow=ulaw
allow=alaw
auth=walkietalkie
aors=walkietalkie

[walkietalkie]
type=auth
auth_type=userpass
password=YourSecurePassword
username=walkietalkie

[walkietalkie]
type=aor
max_contacts=1
```

#### Step 3: Configure Dialplan
Edit `/etc/asterisk/extensions.conf`:
```ini
[incoming]
exten => _X.,1,NoOp(Incoming call from ${CALLERID(num)})
same => n,Answer()
same => n,Record(recordings/${UNIQUEID}.wav)
same => n,agi(agi://localhost:4573/process_call)  ; Your Python script
same => n,Hangup()
```

#### Step 4: Create Python AGI Handler
Create `asterisk_handler.py` in your project:

```python
"""
Asterisk AGI Handler - Replaces Twilio Webhook
"""
import asyncio
from asterisk.agi import AGI
import httpx

async def process_asterisk_call(agi: AGI):
    """Process incoming Asterisk call"""
    # Get caller information
    caller_id = agi.env['agi_callerid']
    unique_id = agi.env['agi_uniqueid']
    
    # Record audio
    agi.answer()
    agi.stream_file('beep')
    agi.record_file(f'recordings/{unique_id}', 'wav', '#', -1, beep=True)
    
    # Send to your AI engine
    async with httpx.AsyncClient() as client:
        with open(f'recordings/{unique_id}.wav', 'rb') as audio:
            response = await client.post(
                'http://localhost:8000/api/transcribe',
                files={'audio': audio},
                data={'caller_id': caller_id, 'source': 'voip'}
            )
    
    # Play confirmation
    if response.status_code == 200:
        agi.stream_file('thank-you')
    
    agi.hangup()

if __name__ == '__main__':
    agi = AGI()
    asyncio.run(process_asterisk_call(agi))
```

#### Step 5: Update Your Application

**Changes to `webhook_handlers.py`:**

```python
class AsteriskWebhookHandler(WebhookHandler):
    """Handles Asterisk AGI requests"""
    
    async def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Asterisk call"""
        return {
            "status": "success",
            "webhook_type": "asterisk_call",
            "caller_id": data.get("caller_id"),
            "recording_path": data.get("recording_path"),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def validate_webhook(self, data: Dict[str, Any], signature: str) -> bool:
        """Validate internal request (local network only)"""
        # For local Asterisk, check IP whitelist
        return True  # Add proper validation
```

**Add route in `AI-CommunicationEngine.py`:**

```python
@app.post("/api/asterisk/webhook")
async def handle_asterisk_call(
    caller_id: str = Form(...),
    recording_path: str = Form(...),
    audio: UploadFile = File(...)
):
    """Handle incoming Asterisk call"""
    audio_data = await audio.read()
    
    # Process through existing pipeline
    result = await middleware.process_audio_stream(
        caller_id=caller_id,
        source=AudioSource.VOIP,
        audio_data=audio_data
    )
    
    return {"status": "success", "task_id": result.task_id}
```

### **Free SIP Providers (for real phone numbers):**

| Provider | Free Tier | Use Case |
|----------|-----------|----------|
| **Twilio SIP** | $1/month DID | Keep one number for testing |
| **Bandwidth.com** | Pay-as-you-go | Cheap US numbers |
| **VoIP.ms** | $0.85/month | Canadian numbers |
| **DIDLogic** | ~$2/month | Global coverage |

---

## 2️⃣ SMS: Twilio SMS → Free Alternatives

### **Option A: Textbelt API (Recommended)**

**Free tier: 1 text/day**
**Paid: $0.002/message (4x cheaper than Twilio)**

```python
"""
Textbelt SMS Service - Replace Twilio SMS
"""
import httpx

class TextbeltSMSService:
    """Free/cheap SMS alternative"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "textbelt"  # "textbelt" = free tier
        self.base_url = "https://textbelt.com/text"
    
    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS via Textbelt"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                data={
                    "phone": phone_number,
                    "message": message,
                    "key": self.api_key
                }
            )
            result = response.json()
            return result.get("success", False)
```

### **Option B: Email-to-SMS Gateways (100% Free)**

Most carriers provide free email-to-SMS gateways:

```python
"""
Email-to-SMS Gateway (Completely Free)
"""
import smtplib
from email.mime.text import MIMEText

SMS_GATEWAYS = {
    "verizon": "@vtext.com",
    "tmobile": "@tmomail.net",
    "att": "@txt.att.net",
    "sprint": "@messaging.sprintpcs.com"
}

async def send_sms_via_email(phone: str, carrier: str, message: str):
    """Send SMS via email gateway (FREE)"""
    email_address = f"{phone}{SMS_GATEWAYS[carrier]}"
    
    msg = MIMEText(message)
    msg['From'] = 'your-email@gmail.com'
    msg['To'] = email_address
    msg['Subject'] = ''  # Empty for SMS
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'app-password')
        server.send_message(msg)
```

### **Option C: Google Voice API (Unofficial)**

Use `pygooglevoice` library (free but unofficial):

```python
from googlevoice import Voice

voice = Voice()
voice.login('email@gmail.com', 'password')
voice.send_sms('+15551234567', 'Your message')
```

**⚠️ Warning:** Against Google TOS, may get banned.

---

## 3️⃣ Push Notifications: Firebase → Keep or Replace

### **Recommendation: KEEP Firebase (Free Tier is Generous)**

Firebase Cloud Messaging (FCM) offers:
- ✅ **Unlimited push notifications** (FREE)
- ✅ Reliable delivery
- ✅ Cross-platform (iOS, Android, Web)

**Monthly Cost: $0** (unless you use other Firebase services)

### **Alternative: Self-Hosted Push (Advanced)**

**OneSignal** - Free alternative:
- ✅ 10,000 subscribers FREE
- ✅ Unlimited notifications
- ✅ Easy integration

```python
"""
OneSignal Push Notifications (Free Alternative)
"""
import httpx

class OneSignalPushService:
    """Free push notification service"""
    
    def __init__(self, app_id: str, api_key: str):
        self.app_id = app_id
        self.api_key = api_key
        self.base_url = "https://onesignal.com/api/v1/notifications"
    
    async def send_push(self, player_ids: list, title: str, body: str):
        """Send push via OneSignal"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={"Authorization": f"Basic {self.api_key}"},
                json={
                    "app_id": self.app_id,
                    "include_player_ids": player_ids,
                    "headings": {"en": title},
                    "contents": {"en": body}
                }
            )
            return response.json()
```

---

## 4️⃣ Walkie-Talkie Integration (Already Free)

Your walkie-talkie integration likely uses:
- Radio hardware with audio interface
- Custom webhook (already in code)

**No changes needed** - this is already free and local.

---

## 📝 Implementation Checklist

### Phase 1: Replace SMS (Easy - 2 hours)
- [ ] Sign up for Textbelt API (or use email-to-SMS)
- [ ] Add new SMS service class to `notification_service.py`
- [ ] Update config to use new provider
- [ ] Test SMS delivery
- [ ] Remove Twilio SMS dependency

### Phase 2: Set Up Asterisk (Medium - 8 hours)
- [ ] Install Asterisk on server
- [ ] Configure SIP trunk
- [ ] Set up dialplan
- [ ] Create AGI handler script
- [ ] Add Asterisk webhook to FastAPI
- [ ] Test call reception and recording
- [ ] Forward audio to transcription service

### Phase 3: Test Everything (Critical - 4 hours)
- [ ] End-to-end test: Call → Transcribe → Task → Notify
- [ ] Load testing (multiple concurrent calls)
- [ ] Failover testing
- [ ] Document new setup

### Phase 4: Cleanup (Easy - 1 hour)
- [ ] Remove Twilio from requirements.txt
- [ ] Update documentation
- [ ] Archive Twilio code (don't delete, keep for reference)

---

## 📈 Cost Comparison

### **Current Setup (All Paid)**
```
Twilio Voice:  $100/month (1000 minutes)
Twilio SMS:    $30/month  (4000 messages)
Firebase:      $0         (free tier)
-------------------------------------------
TOTAL:         $130/month = $1,560/year
```

### **Hybrid Setup (Recommended)**
```
Asterisk:      $0         (self-hosted)
Textbelt:      $8/month   (4000 messages)
Firebase:      $0         (free tier)
Server costs:  $5/month   (small VPS if needed)
-------------------------------------------
TOTAL:         $13/month = $156/year
SAVINGS:       $1,404/year (90% reduction!)
```

### **Fully Free Setup**
```
Asterisk:      $0         (self-hosted)
Email-to-SMS:  $0         (carrier gateways)
OneSignal:     $0         (free tier)
Local server:  $0         (use existing PC)
-------------------------------------------
TOTAL:         $0/month = $0/year
SAVINGS:       $1,560/year (100% free!)
```

---

## 🚀 Quick Start: Minimal Changes for Maximum Savings

If you want to save money RIGHT NOW without major changes:

### 1. Switch to Textbelt SMS (5 minutes)

Add to `.env`:
```
TEXTBELT_API_KEY=your_key_here
SMS_PROVIDER=textbelt
```

Update `config.ini`:
```ini
[sms]
provider = textbelt
api_key = ${TEXTBELT_API_KEY}
```

### 2. Keep Firebase Free Tier (Already Free)
No changes needed - you're already using free tier.

### 3. Minimize Twilio Usage
- Use Twilio only for receiving calls (cheap)
- Don't use Twilio for outbound calls
- Forward calls to Asterisk for processing

**Immediate Savings: ~$30/month**

---

## 🔗 Useful Resources

### Asterisk
- [Official Docs](https://wiki.asterisk.org/)
- [FreePBX](https://www.freepbx.org/) - GUI for Asterisk
- [Incredible PBX](https://www.incrediblepbx.com/) - Preconfigured VM

### SMS Alternatives
- [Textbelt API](https://textbelt.com/)
- [Email-to-SMS Gateways List](https://avtech.com/articles/138/list-of-email-to-sms-addresses/)

### Push Notifications
- [OneSignal Docs](https://documentation.onesignal.com/)
- [FCM Documentation](https://firebase.google.com/docs/cloud-messaging)

### SIP Providers
- [VoIP.ms](https://voip.ms/)
- [Bandwidth.com](https://www.bandwidth.com/)

---

## ❓ FAQ

### Q: Will switching to Asterisk break my existing code?
**A:** No - you just need to add a new webhook handler. Your transcription and task engine remain unchanged.

### Q: Do I need a dedicated server for Asterisk?
**A:** No - it can run on your development machine, a Raspberry Pi, or a $5/month VPS.

### Q: Can I keep Twilio for some things?
**A:** Yes! Use Twilio for incoming calls (cheap) and Asterisk for processing (free).

### Q: Is Asterisk difficult to set up?
**A:** Medium difficulty. If you can run Python and FastAPI, you can learn Asterisk. Allow 1-2 days for learning.

### Q: What if I need production reliability?
**A:** Use a hybrid: Asterisk primary, Twilio failover. Best of both worlds.

---

## 🎯 Recommended Path Forward

**For Your Project, I Recommend:**

### **Month 1: Quick Wins**
1. Replace Twilio SMS with Textbelt (85% cheaper)
2. Keep Firebase (already free)
3. **Savings: $25-30/month**

### **Month 2: Learn Asterisk**
1. Install Asterisk on development machine
2. Test with softphone clients
3. Don't switch production yet

### **Month 3: Hybrid Approach**
1. Use Asterisk for internal testing
2. Keep Twilio as backup
3. Gradually shift traffic
4. **Savings: $80-100/month**

### **Month 4+: Evaluate**
- If Asterisk works well → fully switch
- If not → stay hybrid
- **Total Potential Savings: $120/month = $1,440/year**

---

## 💡 Conclusion

You have **three tiers of options**:

1. **Quick & Easy** (Today): Switch to Textbelt SMS
   - Time: 30 minutes
   - Savings: ~$25/month
   - Difficulty: ⭐☆☆☆☆

2. **Balanced** (This Month): Textbelt + Keep Firebase + Learn Asterisk
   - Time: 2-4 days
   - Savings: ~$100/month  
   - Difficulty: ⭐⭐⭐☆☆

3. **Advanced** (Next Quarter): Full Asterisk + Free SMS/Push
   - Time: 1-2 weeks
   - Savings: ~$130/month
   - Difficulty: ⭐⭐⭐⭐☆

**My Recommendation:** Start with option 1, then move to option 2 as you learn.

---

## 📞 Need Help?

If you get stuck during migration:
1. Check Asterisk logs: `sudo asterisk -rvvv`
2. Test with softphone: [Zoiper](https://www.zoiper.com/) (free)
3. Join [Asterisk community](https://community.asterisk.org/)

---

**Last Updated:** February 2026
**Project Version:** 1.0.0
