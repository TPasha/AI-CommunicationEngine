# System Architecture

## Overview

The AI Communication Engine is a sophisticated middleware system designed to process audio from multiple sources (VoIP, SMS, walkie-talkie), intelligently classify content, automatically create prioritized tasks, and send multi-channel notifications to relevant staff.

## Design Principles

1. **Asynchronous-First**: All I/O operations use async/await for high concurrency
2. **Modular Architecture**: Cleanly separated concerns with minimal coupling
3. **Fallback Systems**: Rule-based fallbacks when AI services are unavailable
4. **Security by Default**: Signature validation, rate limiting, encryption
5. **Observability**: Comprehensive logging, metrics, and tracing
6. **Scalability**: Designed to handle 50+ concurrent streams with sub-second latency

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
                      FastAPI Application                        
├─────────────────────────────────────────────────────────────────┤
                                                                 
  ┌──────────────────────────────────────────────────────────┐  
             Request Routing & Validation                     
    - REST endpoints (/transcribe, /tasks/*, etc.)            
    - WebSocket handler (/ws/audio/{caller_id})               
    - Webhook handlers (/webhooks/*)                          
  └────────────────────┬─────────────────────────────────────┘  
                                                                
  ┌─────────────────────────────────────────────────────────┐  
           Communication Middleware Orchestrator               
    - Audio stream management                                 
    - Pipeline coordination                                   
    - Error handling & circuit breaker                        
  └────────────────────┬─────────────────────────────────────┘  
                                                                
  ┌────────────┬───────┼───────┬──────────┬──────────────────┐  
                                                          
                                                          
 ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐  
  Transcription      Intent             Task Action      
  Service            Classifier         Engine           
                                                         
  • Multi-provider   • LLM-based        • Prioritizer    
  • Batch support    • Rule fallback    • Assigner       
  • 11+ languages    • Entity extract   • PMS sync       
  • Confidence       • Knowledge base   • Escalation     
 └──────────────────┘ └──────────────────┘ └────────────────┘  
                                                                
  ┌─────────────────────────────────────────────────────────┐  
           Notification Service                               
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      
     Push         SMS       Email      Voice         
    (Firebase) (Twilio)    (SMTP)    (Twilio)        
    └──────────┘ └──────────┘ └──────────┘ └──────────┘      
  └─────────────────────────────────────────────────────────┘  
                                                                
  ┌─────────────────────────────────────────────────────────┐  
           Database Layer (SQLAlchemy ORM)                   
    - Transcription records                                  
    - Task management with audit trail                       
    - Staff member profiles & availability                   
    - Inventory status tracking                              
    - Audio session logs                                     
  └─────────────────────────────────────────────────────────┘  
                                                                 
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Pipeline

### Audio Processing Pipeline

```
1. AUDIO INPUT
   ├─ Twilio Voice Call
   ├─ Vonage SMS Message
   ├─ Walkie-Talkie Transmission
   ├─ WebSocket Stream
   └─ REST API Upload

   
   

2. WEBHOOK VALIDATION (Optional)
   ├─ Signature verification
   ├─ Rate limiting
   └─ Source authentication
   
   
   

3. AUDIO STREAM MANAGEMENT
   ├─ Concurrent stream tracking (<= 50 streams)
   ├─ Buffer management
   └─ Timeout handling
   
   
   

4. TRANSCRIPTION SERVICE
   ├─ Provider selection (OpenAI Whisper default)
   ├─ Language detection
   ├─ Audio encoding conversion
   ├─ Confidence scoring
   └─ Error recovery
   
   
   

5. DATABASE STORAGE (Transcription)
   ├─ Save raw text
   ├─ Store confidence score
   ├─ Record speaker/device ID
   └─ Set processing timestamp
   
   
   

6. INTENT CLASSIFICATION
   ├─ Entity extraction (rooms, quantities, urgency)
   ├─ Attempt LLM classification (GPT-4)
     ├─ If timeout/error → Rule-based fallback
     └─ Extract intent type (TASK, INQUIRY, etc.)
   ├─ Check knowledge base (for inquiries)
   └─ Flag for human review if needed
   
   
   

7. UPDATE TRANSCRIPTION RECORD
   ├─ Store intent type
   ├─ Set review flag
   └─ Store extracted entities
   
   
   

8. INTENT-SPECIFIC ROUTING
   
   ├─ TASK Intent
     
     
     TASK ACTION ENGINE
     ├─ Extract task description
     ├─ Calculate priority (1-5)
       ├─ Urgency level (40%)
       ├─ Inventory status (20%)
       ├─ Staff workload (20%)
       └─ Time sensitivity (20%)
     ├─ Find best assignee
       ├─ Department match
       ├─ Skill matching
       ├─ Availability check
       └─ Workload balancing
     ├─ Create task record
     ├─ Set due date (based on priority)
     └─ Store in database
     
     
     NOTIFICATION DISPATCH
     ├─ Get staff preferences
     ├─ Select channels (based on priority)
       ├─ LOW: Push, Email
       ├─ NORMAL: Push, SMS
       ├─ HIGH: SMS, Push
       └─ URGENT: Voice, SMS, Push
     └─ Send notifications
   
   ├─ INQUIRY Intent
     
     
     KNOWLEDGE BASE LOOKUP
     ├─ Search FAQ database
     ├─ Generate response
     └─ Send response back
   
   └─ OTHER Intent
      
      
      LOG & ARCHIVE
      (for human review)

   
   

9. RESPONSE TO CLIENT
   ├─ Return transcription ID
   ├─ Confirmation of action taken
   └─ Status/error information
```

## Module Descriptions

### 1. Transcription Service (`transcription_service.py`)

**Purpose**: Convert audio to text using multiple providers

**Key Classes**:
- `TranscriptionService`: Main service orchestrator
- `TranscriptionResult`: Return data structure
- `BatchTranscriptionService`: Process multiple streams concurrently
- `TranscriptionProvider`: Enum of available providers

**Features**:
- Multi-provider support (OpenAI Whisper, Google Cloud, Azure, AWS, Local)
- Concurrent processing with semaphore limiting
- Confidence scoring
- Language-specific handling
- Error recovery with provider fallback

**Performance**:
- Single audio file: ~2-5 seconds (1-minute audio)
- Concurrent batch: Linear scaling up to 50 streams

### 2. Intent Classifier (`intent_classifier.py`)

**Purpose**: Determine intent and extract relevant entities from transcriptions

**Key Classes**:
- `IntentClassifier`: LLM-based classification with rule fallback
- `EntityExtractor`: Regex-based entity extraction
- `IntentClassification`: Result data structure
- `HotelKnowledgeBase`: Built-in Q&A database

**Features**:
- Dual-path classification (LLM + rules)
- Entity extraction for: room numbers, quantities, urgency, people, items
- Knowledge base for common inquiries
- Confidence scoring
- Automatic escalation detection

**Entity Types**:
```python
{
    "room_number": "301",           # Regex: r'\b([1-9]\d{2}|[1-9]\d)\b'
    "quantity": 5,                  # Regex: r'(\d+)\s*(?:extra|additional)'
    "urgency_level": 4,             # Keywords: urgent, asap, immediately, etc.
    "item_required": "towels",      # Pattern matching on item keywords
    "people_mentioned": ["John"],   # Name extraction
    "location": "main lobby"        # Location keywords
}
```

### 3. Task Action Engine (`task_action_engine.py`)

**Purpose**: Create, prioritize, assign, and manage tasks

**Key Classes**:
- `TaskActionEngine`: Main orchestrator
- `TaskPrioritizer`: Multi-factor priority calculation
- `TaskAssigner`: Intelligent staff assignment

**Priority Calculation**:
```
Priority = (
    (urgency_level / 5) * 0.40 +        // Urgency weight
    inventory_score * 0.20 +             // Is item available?
    (1 - staff_load) * 0.20 +            // Staff workload
    time_sensitivity * 0.20              // Is it time-sensitive?
) * 5

Final: Rounded to 1-5 scale
```

**Assignee Selection**:
1. Filter by department
2. Apply skill requirements
3. Consider availability status
4. Balance workload

### 4. Notification Service (`notification_service.py`)

**Purpose**: Send multi-channel notifications with intelligent routing

**Key Classes**:
- `NotificationService`: Main orchestrator
- `PushNotificationService`: Firebase Cloud Messaging
- `SMSNotificationService`: Twilio SMS
- `EmailNotificationService`: SMTP
- `VoiceNotificationService`: Twilio Voice
- `NotificationRouter`: Channel selection logic

**Channel Selection**:
```python
Priority → Channels
---------   --------
LOW        → [PUSH, EMAIL]
NORMAL     → [PUSH, SMS]
HIGH       → [SMS, PUSH]
URGENT     → [VOICE, SMS, PUSH]

Modified by:
- Staff availability (off_duty → less intrusive)
- Staff preferences (JSON)
- Previous engagement (optional)
```

### 5. Webhook Handlers (`webhook_handlers.py`)

**Purpose**: Accept and validate webhooks from external systems

**Key Classes**:
- `TwilioWebhookHandler`: Handles Twilio voice/SMS
- `VonageWebhookHandler`: Handles Vonage/Nexmo webhooks
- `WalkieTalkieWebhookHandler`: Custom radio protocol
- `WebhookRouter`: Routes to appropriate handler

**Validation Methods**:
- Twilio: RequestValidator with X-Twilio-Signature
- Vonage: MD5(sorted_params + secret)
- Custom: HMAC-SHA256(payload, api_key)

### 6. Database Models (`models.py`)

**Purpose**: Define database schema and relationships

**Key Tables**:
- `Transcription`: Audio to text records
- `Task`: Created tasks with status
- `TaskStatusUpdate`: Audit trail
- `InquiryResponse`: FAQ responses
- `StaffMember`: Employee profiles
- `InventoryStatus`: Item tracking
- `AudioStreamSession`: Call logs

**Relationships**:
```
Transcription
├─ 1:N → Task
└─ 1:1 → IntentType

Task
├─ 1:N → TaskStatusUpdate
├─ M:1 → StaffMember (assigned_to)
├─ M:1 → Transcription
└─ M:1 → StaffMember (completed_by)

StaffMember
├─ 1:N → Task (assigned_to)
├─ 1:N → TaskStatusUpdate (updated_by)
└─ 1:N → AudioStreamSession (device)
```

### 7. Main Application (`AI-CommunicationEngine.py`)

**Purpose**: FastAPI application tying all components together

**Key Components**:
- REST API endpoints
- WebSocket handler for streaming
- Webhook registration
- Configuration loading
- Middleware initialization

**REST Endpoints**:
```
GET  /health
     Check service status

POST /transcribe
     Submit audio for processing

POST /webhooks/{source}
     Receive webhooks from VoIP/radio systems

GET  /streams
     List active audio streams

GET  /tasks/{id}
PUT  /tasks/{id}/status
     Task management

WS   /ws/audio/{caller_id}
     Real-time audio streaming
```

## Concurrency Model

### AsyncIO Architecture

```
┌─────────────────────────────┐
   FastAPI/Uvicorn (ASGI)   
   - 1-N worker threads      
   - Async event loop        
└────────────┬────────────────┘
             
    ┌────────┴────────┐
                     
                     
┌────────────┐  ┌────────────┐
 Handler 1     Handler 2  
 Processing    Processing 
└────────────┘  └────────────┘
                     
    ├─────────┬───────┤
                    
                    
┌──────┐  ┌──────┐  ┌──────┐
Call A  Call B  Call C
 Txn     Txn     Txn  
└──────┘  └──────┘  └──────┘
```

### Stream Management

```
AudioStreamManager
├─ active_streams: Dict[str, StreamData]
├─ semaphore: Semaphore(50)  # Max concurrent
├─ add_stream()
├─ remove_stream()
├─ add_chunk()
└─ get_stream_info()

Chunk Receipt:
1. Check semaphore (permit)
2. Add to stream buffer
3. Check buffer size
4. Process when complete/timeout
5. Release semaphore
```

## Error Handling & Resilience

### Fallback Chain

```
Intent Classification:
├─ Attempt: LLM (GPT-4) with timeout
├─ If timeout/error
  └─ Fallback: Rule-based regex
     ├─ If finds match → Use rules
     └─ If no match → Mark for human review
└─ If no response → Generic response + flag

Transcription:
├─ Attempt: OpenAI Whisper
├─ If fails
  └─ Fallback: Google Cloud Speech
     ├─ If fails
       └─ Fallback: Azure Speech
          ├─ If fails
            └─ Return error (no fallback)
```

### Rate Limiting

```
Per IP: 100 requests/minute
Per API key: 1000 requests/hour
Global: 10,000 requests/minute
Backpressure: Return 429 Too Many Requests
```

## Security Architecture

### Authentication & Authorization

```
REST API
├─ Public endpoints: /health, /webhooks/*
├─ Protected endpoints: /transcribe, /tasks/*
  └─ API key in header: X-API-Key
└─ Rate limiting per key

WebSocket
├─ Token-based auth
├─ Origin validation
└─ Connection timeout

Webhooks
├─ Signature validation (per provider)
├─ IP whitelisting (optional)
├─ Replay attack prevention (timestamps)
└─ HTTPS required (production)
```

### Data Protection

```
Transit: TLS 1.3 (HTTPS/WSS)
At Rest: Database encryption (optional)
         - SQLite can use sqlcipher
         - PostgreSQL with pgcrypto
In Memory: No sensitive data logged
Secrets: Environment variables (.env)
         - NOT in source code
         - NOT in git history
```

## Performance Optimization

### Caching

```
LRU Cache (99 entries):
├─ Intent classification results
├─ Staff member queries
└─ Inventory lookups

TTL Cache:
├─ Knowledge base answers (24 hours)
├─ Staff availability (5 minutes)
└─ Vocabulary/models (1 hour)
```

### Database Optimization

```
Indexes:
├─ transcription(speaker_id, created_at)
├─ task(assigned_to, status)
├─ task(due_date PARTIAL status='pending')
├─ staff_member(department, availability_status)
└─ inventory_status(item_name)

Connection Pooling:
├─ SQLAlchemy pool_size: 20
├─ max_overflow: 40
└─ pool_recycle: 3600 seconds
```

### Monitoring & Metrics

```
Application Metrics:
├─ Audio processed (events/min)
├─ Tasks created (events/min)
├─ Notification sent (count/type)
├─ Latency (p50, p95, p99)
└─ Error rate (%)

Database Metrics:
├─ Query count & duration
├─ Connection pool usage
├─ Transaction rollbacks
└─ Slow query log (>1s)

System Metrics:
├─ CPU usage (%)
├─ Memory usage (bytes)
├─ Active connections
└─ File descriptors
```

## Deployment Topology

### Single-Machine Deployment

```
┌────────────────────────────┐
   Single Server (AWS EC2)  
├────────────────────────────┤
 Nginx (reverse proxy)      
 80/443 → :8000            
├────────────────────────────┤
 AI Engine (4 workers)      
 Uvicorn + Gunicorn        
├────────────────────────────┤
 SQLite Database            
 /data/engine.db            
├────────────────────────────┤
 Redis (optional)           
 Rate limiting, sessions    
└────────────────────────────┘
```

### Scalable Deployment

```
┌─────────────────┐
 Load Balancer   
 (ALB/NLB)       
└────────┬────────┘
         
    ┌────┴─────┐
               
               
┌──────────┐ ┌──────────┐
Engine-1   Engine-2  
(port      (port     
8001)      8002)     
└────┬─────┘ └────┬─────┘
                
     └────┬──────┘
          
     ┌──────────┐
      PostgreSQL 
      (RDS)      
     └────────────┘

Async Queue (optional):
├─ Task processing
├─ Bulk notifications
║─ Report generation
└─ Data archival
```

## Configuration Management

### Environment Hierarchy

```
1. Defaults (hardcoded in code)
2. config.ini (file)
3. Environment variables (.env)
4. CLI arguments (at startup)

Override order (lowest to highest):
code → config.ini → .env → CLI
```

### Configuration Validation

```
At startup:
├─ Check all required variables present
├─ Validate API key formats
├─ Test database connectivity
├─ Verify file permissions
├─ Check resource limits
└─ Log configuration summary (redacted)
```

---

**See README.md for usage and QUICKSTART.md for getting started.**
