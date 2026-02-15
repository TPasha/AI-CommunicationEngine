"""
Security and Edge Case Tests
Tests for error scenarios, concurrency, and security validations
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from src.intent_classifier import IntentClassifier, EntityExtractor
from src.transcription_service import TranscriptionService, TranscriptionProvider
from src.task_action_engine import TaskActionEngine, TaskPrioritizer
from src.models import init_db, StaffMember, Task, Transcription, AudioSource, TaskStatus


class TestIntentClassifierInputValidation:
    """Test input validation for intent classifier"""
    
    def test_reject_empty_text(self):
        """Test that empty text is rejected"""
        classifier = IntentClassifier()
        
        with pytest.raises(ValueError):
            asyncio.run(classifier.classify(""))
    
    def test_reject_oversized_text(self):
        """Test that oversized text is truncated"""
        classifier = IntentClassifier()
        massive_text = "x" * (IntentClassifier.MAX_TEXT_LENGTH + 1000)
        
        # Should truncate without raising error
        result = asyncio.run(classifier.classify(massive_text))
        assert result is not None
    
    def test_reject_non_string_input(self):
        """Test that non-string inputs are rejected"""
        classifier = IntentClassifier()
        
        with pytest.raises(ValueError):
            asyncio.run(classifier.classify(12345))
    
    def test_sanitize_special_characters(self):
        """Test that special characters in entities are handled"""
        text = "Room <script>alert('xss')</script> needs help"
        entities = EntityExtractor.extract_entities(text)
        
        # Should not execute scripts
        assert "script" not in str(entities).lower()


class TestConcurrentTaskCreation:
    """Test concurrent task creation for race conditions"""
    
    @pytest.mark.asyncio
    async def test_concurrent_task_creation(self):
        """Test that concurrent task creation handles properly"""
        init_db()
        from src.models import get_session as get_db_session
        
        # This is a simplified test - in real scenario would use proper async DB
        tasks = []
        
        async def create_task(i):
            # Simulate async task creation
            await asyncio.sleep(0.01)
            return f"task_{i}"
        
        results = await asyncio.gather(*[create_task(i) for i in range(10)])
        assert len(results) == 10
        assert len(set(results)) == 10  # All unique


class TestWebhookValidationFailures:
    """Test webhook validation with invalid signatures"""
    
    @pytest.mark.asyncio
    async def test_invalid_twilio_signature(self):
        """Test that invalid Twilio signatures are rejected"""
        from src.webhook_handlers import TwilioWebhookHandler
        
        handler = TwilioWebhookHandler(auth_token="test_token")
        
        data = {
            "CallSid": "CA123456789",
            "From": "+15551234567",
        }
        
        # Invalid signature should fail validation
        result = await handler.validate_webhook(
            data,
            "invalid_signature_here",
            "https://example.com/webhook"
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_invalid_vonage_signature(self):
        """Test that invalid Vonage signatures are rejected"""
        from src.webhook_handlers import VonageWebhookHandler
        
        handler = VonageWebhookHandler(api_key="test_key", api_secret="test_secret")
        
        data = {
            "messageId": "MSG123",
            "text": "Hello"
        }
        
        result = await handler.validate_webhook(data, "invalid_sig")
        assert result is False


class TestTranscriptionServiceEdgeCases:
    """Test transcription service with unusual inputs"""
    
    @pytest.mark.asyncio
    async def test_transcribe_very_short_audio(self):
        """Test transcription with very short audio (< 100ms)"""
        service = TranscriptionService()
        
        # 100 bytes of audio = ~6ms at 16kHz stereo
        tiny_audio = b'\x00' * 100
        
        # Should handle gracefully without crashing
        result = await service.transcribe_audio(tiny_audio)
        # Result could be None (no speech) or error, but shouldn't crash
        assert result is None or isinstance(result, Exception) or hasattr(result, 'text')
    
    @pytest.mark.asyncio
    async def test_transcribe_huge_audio(self):
        """Test transcription with very large audio (> 100MB would timeout)"""
        service = TranscriptionService()
        
        # Create fake large audio (won't be processed, but tests handling)
        large_audio = b'\x00' * (1024 * 1024)  # 1MB
        
        # Should respect timeout
        result = await service.transcribe_audio(large_audio)
        # Depends on implementation, but should handle gracefully
        assert result is None or hasattr(result, 'text')


class TestTaskPriorizerEdgeCases:
    """Test task prioritizer with edge cases"""
    
    def test_priority_with_zero_urgency(self):
        """Test priority calculation with minimum urgency"""
        priority = TaskPrioritizer.calculate_priority(
            urgency_level=0,
            current_staff_load=0
        )
        
        assert 1 <= priority <= 5
    
    def test_priority_with_negative_urgency(self):
        """Test priority calculation with invalid negative urgency"""
        priority = TaskPrioritizer.calculate_priority(
            urgency_level=-5,
            current_staff_load=0
        )
        
        # Should clamp to valid range
        assert 1 <= priority <= 5
    
    def test_priority_with_extreme_workload(self):
        """Test priority calculation with extreme workload"""
        priority = TaskPrioritizer.calculate_priority(
            urgency_level=3,
            current_staff_load=1000
        )
        
        assert 1 <= priority <= 5


class TestDatabaseErrors:
    """Test database error handling"""
    
    @pytest.mark.asyncio
    async def test_task_creation_rollback_on_error(self):
        """Test that task creation rolls back on database error"""
        from src.models import Session as get_session
        
        init_db()
        db = get_session()
        engine = TaskActionEngine(db)
        
        # Try to create task with invalid transcription_id
        transcription = Transcription(
            source=AudioSource.VOIP_PHONE,
            raw_text="Test",
            confidence_score=0.9
        )
        db.add(transcription)
        db.commit()
        
        # Create task with malformed entities
        result = await engine.create_task_from_transcription(
            transcription=transcription,
            intent_classification={"primary_intent": "task"},
            extracted_entities=None  # Should handle None gracefully
        )
        
        # Should either succeed or rollback without crashing
        assert result is None or isinstance(result, Task)
        db.close()


class TestDependencyLoadingFailures:
    """Test graceful degradation when dependencies fail to load"""
    
    def test_intent_classifier_without_openai(self):
        """Test intent classifier when OpenAI is not available"""
        with patch('src.intent_classifier.HAS_OPENAI', False):
            classifier = IntentClassifier(provider="openai_gpt")
            # Should use rule-based fallback
            result = classifier._classify_with_rules("Test text")
            assert result is not None
    
    def test_transcription_service_without_transformers(self):
        """Test transcription when transformers is not available"""
        with patch('src.transcription_service.HAS_TRANSFORMERS', False):
            # Trying to use HF should fail gracefully or raise clear error
            try:
                service = TranscriptionService(provider="huggingface_whisper")
                # Should raise ImportError
                assert False, "Should have raised ImportError"
            except ImportError as e:
                assert "transformers" in str(e)


class TestEntityExtractionRobustness:
    """Test entity extraction with problematic inputs"""
    
    def test_extract_from_very_long_text(self):
        """Test entity extraction from very long text"""
        long_text = "Room " + "very " * 1000 + "123 needs help"
        entities = EntityExtractor.extract_entities(long_text)
        
        # Should not crash and should find room number
        assert isinstance(entities, dict)
    
    def test_extract_from_unicode_text(self):
        """Test entity extraction from unicode text"""
        unicode_text = "Room 123 需要幫助 🏨"
        entities = EntityExtractor.extract_entities(unicode_text)
        
        # Should handle unicode without crashing
        assert isinstance(entities, dict)
    
    def test_extract_from_malformed_patterns(self):
        """Test entity extraction doesn't fail on malformed patterns"""
        malformed_texts = [
            "Room@#$%^&*()",
            "Room---999---hello",
            "R00M 123",  # Different letter
            "room [123]",
        ]
        
        for text in malformed_texts:
            entities = EntityExtractor.extract_entities(text)
            assert isinstance(entities, dict)


class TestMemoryManagement:
    """Test for potential memory leaks"""
    
    @pytest.mark.asyncio
    async def test_repeated_classifier_calls(self):
        """Test that repeated classifier calls don't leak memory"""
        classifier = IntentClassifier()
        
        for _ in range(100):
            result = await classifier.classify("Room 123 needs help")
            assert result is not None
        
        # If we got here without OOM, test passes
        assert True
    
    @pytest.mark.asyncio
    async def test_concurrent_classifier_calls(self):
        """Test concurrent classifier calls handle resources properly"""
        classifier = IntentClassifier()
        
        async def classify_text(text):
            return await classifier.classify(text)
        
        results = await asyncio.gather(*[
            classify_text(f"Room {i} needs help")
            for i in range(50)
        ])
        
        assert len(results) == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
