#!/usr/bin/env python3
"""
Quick test script to validate Hugging Face intent classification integration
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from intent_classifier import IntentClassifier

async def test_hf_intent():
    print("[TEST] Initializing Hugging Face intent classifier...")
    try:
        classifier = IntentClassifier(
            provider="huggingface",
            model="facebook/bart-large-mnli",
            temperature=0.5,
            max_tokens=500,
            timeout_ms=30000  # 30 seconds for first run
        )
        print("[OK] Intent classifier initialized successfully")
        test_text = "I need towels in room 302 immediately"
        print(f"[TEST] Classifying: {test_text}")
        result = await classifier.classify(test_text, speaker_id="guest_123")
        if result is None:
            print("[FAIL] Classification returned None (timeout or error)")
            return False
        print(f"[OK] Intent: {result.intent_type.value}")
        print(f"[OK] Confidence: {result.confidence:.2f}")
        print(f"[OK] Priority: {result.suggested_priority}")
        print(f"[OK] Entities: {result.extracted_entities}")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_hf_intent())
    sys.exit(0 if success else 1)
