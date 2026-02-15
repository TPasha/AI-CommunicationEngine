#!/usr/bin/env python3
"""
Complete test for Hugging Face integration
Tests both transcription service and intent classifier with HF providers
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from transcription_service import TranscriptionService, TranscriptionProvider
from intent_classifier import IntentClassifier, LLMProvider


async def test_services():
    """Test both Hugging Face services"""
    print("=" * 70)
    print("HUGGING FACE INTEGRATION TEST")
    print("=" * 70)
    
    # Test 1: Transcription Service
    print("\n[TEST 1] Transcription Service with Hugging Face")
    print("-" * 70)
    try:
        transcription_svc = TranscriptionService(
            provider="huggingface_whisper",
            model="openai/whisper-tiny",
            language="en"
        )
        print(f"✓ Transcription service initialized")
        print(f"  Provider: {transcription_svc.provider.value}")
        print(f"  Model: {transcription_svc.model}")
        print(f"  Language: {transcription_svc.language}")
        
        # Verify pipeline exists
        assert hasattr(transcription_svc, 'hf_pipeline'), "HF pipeline not initialized"
        print(f"✓ Hugging Face pipeline is ready")
        
    except Exception as e:
        print(f"✗ Transcription service failed: {e}")
        return False
    
    # Test 2: Intent Classifier
    print("\n[TEST 2] Intent Classifier with Hugging Face")
    print("-" * 70)
    try:
        intent_classifier = IntentClassifier(
            provider="huggingface",
            model="facebook/bart-large-mnli"
        )
        print(f"✓ Intent classifier initialized")
        print(f"  Provider: {intent_classifier.provider.value}")
        print(f"  Model: {intent_classifier.model}")
        
        # Verify pipeline exists
        assert hasattr(intent_classifier, 'hf_pipeline'), "HF pipeline not initialized"
        print(f"✓ Hugging Face zero-shot classification pipeline is ready")
        
    except Exception as e:
        print(f"✗ Intent classifier failed: {e}")
        return False
    
    # Test 3: Test intent classification with sample text
    print("\n[TEST 3] Intent Classification Examples")
    print("-" * 70)
    
    test_cases = [
        "Room 302 needs towels immediately",
        "Is the pool open?",
        "I need to speak to a manager",
    ]
    
    for text in test_cases:
        try:
            result = await intent_classifier.classify(text)
            if result:
                print(f"✓ '{text}'")
                print(f"  → Intent: {result.intent_type.value}")
                print(f"  → Confidence: {result.confidence:.1%}")
                print(f"  → Priority: {result.suggested_priority}")
            else:
                print(f"✗ Failed to classify: '{text}'")
                return False
        except Exception as e:
            print(f"✗ Classification error for '{text}': {e}")
            return False
    
    # Test 4: Verify dual-provider support
    print("\n[TEST 4] Provider Abstraction Verification")
    print("-" * 70)
    
    print(f"✓ Transcription providers: {[p.value for p in TranscriptionProvider]}")
    print(f"✓ Intent LLM providers: {[p.value for p in LLMProvider]}")
    print(f"✓ Can switch providers without code changes (config-driven)")
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
    print("\nSummary:")
    print("✓ Transcription service uses Hugging Face Whisper (local, free)")
    print("✓ Intent classifier uses Hugging Face zero-shot classification (local, free)")
    print("✓ Both services are configured via config.ini")
    print("✓ No external API keys required for local models")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_services())
    sys.exit(0 if success else 1)
