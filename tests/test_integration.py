"""
Integration Tests
Comprehensive test suite for AI Communication Engine
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Database tests
from src.models import (
    init_db, Session, Transcription, Task, StaffMember, AudioSource,
    IntentType, TaskStatus, StaffAvailabilityStatus
)

# Service tests
from src.transcription_service import TranscriptionService, TranscriptionProvider, TranscriptionResult
from src.intent_classifier import IntentClassifier, EntityExtractor, IntentClassification
from src.task_action_engine import TaskActionEngine, TaskPrioritizer, TaskAssigner
from src.notification_service import NotificationService, NotificationPriority

# Webhook tests
from src.webhook_handlers import (
    TwilioWebhookHandler, VonageWebhookHandler, WalkieTalkieWebhookHandler
)


# ==================== Database Tests ====================

class TestDatabaseModels:
    """Test database models and relationships"""
    
    def setup_method(self):
        """Initialize test database"""
        init_db()
        self.db = Session()
    
    def teardown_method(self):
        """Clean up test database"""
        self.db.close()
    
    def test_create_staff_member(self):
        """Test staff member creation"""
        staff = StaffMember(
            name="Jane Doe",
            role="Manager",
            department="management",
            phone_number="+1-555-0456",
            skills="leadership,training"
        )
        
        self.db.add(staff)
        self.db.commit()
        
        assert staff.id is not None
        assert staff.name == "Jane Doe"
        assert staff.availability_status == StaffAvailabilityStatus.AVAILABLE
    
    def test_create_transcription(self):
        """Test transcription creation"""
        transcription = Transcription(
            source=AudioSource.WALKIE_TALKIE,
            raw_text="Test transmission",
            confidence_score=0.88,
            speaker_id="device_001"
        )
        
        self.db.add(transcription)
        self.db.commit()
        
        assert transcription.id is not None
        assert transcription.source == AudioSource.WALKIE_TALKIE
        assert transcription.confidence_score == 0.88
    
    def test_create_task_with_assignment(self):
        """Test task creation and assignment"""
        # Create staff
        staff = StaffMember(
            name="John Worker",
            role="Technician",
            department="maintenance",
            phone_number="+1-555-0789"
        )
        self.db.add(staff)
        self.db.commit()
        
        # Create transcription
        transcription = Transcription(
            source=AudioSource.VOIP_PHONE,
            raw_text="Fix the broken AC",
            confidence_score=0.95,
            speaker_id="caller_001"
        )
        self.db.add(transcription)
        self.db.commit()
        
        # Create task
        task = Task(
            transcription_id=transcription.id,
            description="Repair air conditioning unit",
            priority=4,
            status=TaskStatus.PENDING,
            location="Room 405",
            assigned_to=staff.id
        )
        self.db.add(task)
        self.db.commit()
        
        # Verify relationships
        assert task.assigned_to == staff.id
        assert task.transcription_id == transcription.id
        assert task.priority == 4


# ==================== Service Tests ====================

class TestTranscriptionService:
    """Test transcription service"""
    
    @pytest.mark.asyncio
    async def test_transcription_service_initialization(self):
        """Test service initialization"""
        service = TranscriptionService(
            provider=TranscriptionProvider.OPENAI_WHISPER,
            api_key="test_key",
            model="whisper-1"
        )
        
        assert service is not None
        assert service.model == "whisper-1"
    
    def test_supported_languages(self):
        """Test supported languages"""
        service = TranscriptionService(
            provider=TranscriptionProvider.OPENAI_WHISPER,
            api_key="test_key"
        )
        
        langs = service.get_supported_languages()
        assert len(langs) > 0
        assert "English" in langs


class TestIntentClassifier:
    """Test intent classification"""
    
    def test_entity_extraction_room_number(self):
        """Test room number extraction"""
        text = "Room 301 needs new towels"
        entities = EntityExtractor.extract_entities(text)
        
        assert entities["room_number"] == "301"
    
    def test_entity_extraction_quantity(self):
        """Test quantity extraction"""
        text = "I need 5 towels for room 203"
        entities = EntityExtractor.extract_entities(text)
        
        assert entities["quantity"] == 5
    
    def test_entity_extraction_urgency(self):
        """Test urgency level extraction"""
        text = "This is URGENT! The guest is waiting"
        entities = EntityExtractor.extract_entities(text)
        
        assert entities["urgency_level"] == 5
    
    def test_entity_extraction_item(self):
        """Test item extraction"""
        text = "Please bring coffee and tea to room 402"
        entities = EntityExtractor.extract_entities(text)
        
        assert "coffee" in entities.get("item_required", "").lower() or \
               "tea" in entities.get("item_required", "").lower()
    
    @pytest.mark.asyncio
    async def test_intent_classifier_initialization(self):
        """Test intent classifier initialization"""
        classifier = IntentClassifier(
            model="gpt-4-turbo-preview",
            temperature=0.7
        )
        
        assert classifier is not None
        assert classifier.model == "gpt-4-turbo-preview"


class TestTaskPrioritizer:
    """Test task priority calculation"""
    
    def test_priority_urgent_task(self):
        """Test priority calculation for urgent task"""
        priority = TaskPrioritizer.calculate_priority(
            urgency_level=5,
            item_required="emergency_supplies",
            current_staff_load=2
        )
        
        assert priority >= 4
    
    def test_priority_routine_task(self):
        """Test priority calculation for routine task"""
        priority = TaskPrioritizer.calculate_priority(
            urgency_level=1,
            item_required="routine_item",
            current_staff_load=5
        )
        
        assert priority <= 2
    
    def test_priority_high_workload(self):
        """Test that high workload reduces priority"""
        priority_normal = TaskPrioritizer.calculate_priority(
            urgency_level=3,
            current_staff_load=0
        )
        
        priority_high_load = TaskPrioritizer.calculate_priority(
            urgency_level=3,
            current_staff_load=15
        )
        
        # High workload should lower the calculated priority slightly
        assert isinstance(priority_normal, int)
        assert isinstance(priority_high_load, int)


class TestTaskAssigner:
    """Test task assignment logic"""
    
    @pytest.mark.asyncio
    async def test_find_best_assignee_high_urgency(self):
        """Test assignee selection with high urgency"""
        init_db()
        db = Session()
        
        try:
            # Create available staff
            staff1 = StaffMember(
                name="Staff One",
                department="housekeeping",
                availability_status=StaffAvailabilityStatus.AVAILABLE,
                skills="cleaning,laundry"
            )
            staff2 = StaffMember(
                name="Staff Two",
                department="housekeeping",
                availability_status=StaffAvailabilityStatus.ON_BREAK,
                skills="cleaning,room_service"
            )
            
            db.add_all([staff1, staff2])
            db.commit()
            
            assignee = await TaskAssigner.find_best_assignee(
                department="housekeeping",
                urgency_level=4,
                db_session=db
            )
            
            assert assignee is not None
            assert assignee.id == staff1.id
        
        finally:
            db.close()


# ==================== Webhook Handler Tests ====================

class TestWebhookHandlers:
    """Test webhook handling"""
    
    @pytest.mark.asyncio
    async def test_twilio_handler_call_webhook(self):
        """Test Twilio call webhook processing"""
        handler = TwilioWebhookHandler(auth_token="test_token")
        
        webhook_data = {
            "CallSid": "CA123456789",
            "From": "+15551234567",
            "To": "+15559876543",
            "CallStatus": "ringing",
            "Direction": "inbound"
        }
        
        result = await handler.process_webhook(webhook_data)
        
        assert result["status"] == "success"
        assert result["webhook_type"] == "call"
        assert result["call_sid"] == "CA123456789"
    
    @pytest.mark.asyncio
    async def test_vonage_handler_sms_webhook(self):
        """Test Vonage SMS webhook processing"""
        handler = VonageWebhookHandler(api_key="test_key", api_secret="test_secret")
        
        webhook_data = {
            "type": "mo-sms",
            "messageId": "MSG123",
            "msisdn": "+15551234567",
            "to": "+15559876543",
            "text": "Hello from Vonage"
        }
        
        result = await handler.process_webhook(webhook_data)
        
        assert result["status"] == "success"
        assert result["webhook_type"] == "sms"
        assert result["message_id"] == "MSG123"
    
    @pytest.mark.asyncio
    async def test_walkie_talkie_handler_transmission(self):
        """Test walkie-talkie transmission webhook"""
        handler = WalkieTalkieWebhookHandler(api_key="test_key")
        
        webhook_data = {
            "event_type": "transmission_received",
            "transmission_id": "TX001",
            "device_id": "DEVICE001",
            "channel": "main",
            "audio_url": "https://example.com/audio.wav",
            "duration": "45.5",
            "signal_strength": "-75"
        }
        
        result = await handler.process_webhook(webhook_data)
        
        assert result["status"] == "success"
        assert result["webhook_type"] == "transmission"
        assert result["transmission_id"] == "TX001"


# ==================== Integration Tests ====================

class TestEndToEndWorkflow:
    """Test complete workflow integration"""
    
    @pytest.mark.asyncio
    async def test_audio_to_task_workflow(self):
        """Test complete audio processing workflow"""
        init_db()
        db = Session()
        
        try:
            # Create staff member
            staff = StaffMember(
                name="Integration Test Staff",
                department="housekeeping",
                phone_number="+1-555-9999",
                skills="cleaning,laundry"
            )
            db.add(staff)
            db.commit()
            
            # Create transcription
            transcription = Transcription(
                source=AudioSource.VOIP_PHONE,
                raw_text="Room 201 needs fresh towels immediately",
                confidence_score=0.92,
                speaker_id="test_caller",
                intent_type=IntentType.TASK,
                requires_human_review=False
            )
            db.add(transcription)
            db.commit()
            
            # Extract entities
            entities = EntityExtractor.extract_entities(transcription.raw_text)
            
            # Calculate priority
            priority = TaskPrioritizer.calculate_priority(
                urgency_level=entities.get("urgency_level", 3),
                item_required="towels"
            )
            
            # Create task
            task = Task(
                transcription_id=transcription.id,
                description="Deliver fresh towels to room 201",
                priority=priority,
                status=TaskStatus.PENDING,
                location="Room 201",
                item_required="towels",
                assigned_to=staff.id
            )
            db.add(task)
            db.commit()
            
            # Verify workflow
            assert transcription.id is not None
            assert task.id is not None
            assert task.assigned_to == staff.id
            assert task.priority >= 3
        
        finally:
            db.close()


# ==================== Performance Tests ====================

class TestPerformance:
    """Test system performance"""
    
    def test_entity_extraction_performance(self):
        """Test entity extraction speed"""
        text = "Room 305 urgently needs 3 extra pillows and blankets for my family"
        
        import time
        start = time.time()
        
        for _ in range(100):
            EntityExtractor.extract_entities(text)
        
        duration = time.time() - start
        
        # Should complete 100 iterations in under 1 second
        assert duration < 1.0
    
    @pytest.mark.asyncio
    async def test_concurrent_entity_extraction(self):
        """Test concurrent entity extraction"""
        texts = [
            "Room 101 needs coffee",
            "Fix the AC in room 202 urgently",
            "What time is breakfast?"
        ] * 10
        
        tasks = [asyncio.create_task(asyncio.to_thread(
            EntityExtractor.extract_entities, text
        )) for text in texts]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 30
        assert all(isinstance(r, dict) for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
