"""
Demo Script
Demonstrates the AI Communication Engine in action
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add parent directory to path so we can import from src/
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import init_db, get_session, Transcription, Task, StaffMember, AudioSource, IntentType, TaskStatus, Base
from src.transcription_service import TranscriptionService, TranscriptionProvider
from src.intent_classifier import IntentClassifier
from src.task_action_engine import TaskActionEngine, TaskPrioritizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_transcription():
    """Demo: Transcription Service"""
    print("\n" + "="*60)
    print("DEMO 1: Transcription Service")
    print("="*60)
    
    service = TranscriptionService(
        provider=TranscriptionProvider.OPENAI_WHISPER,
        api_key="sk-your-api-key-here",
        model="whisper-1"
    )
    
    print("[OK] Transcription service initialized")
    print("[OK] Provider: OpenAI Whisper")
    print("[OK] Model: whisper-1")
    print("[OK] Supported languages: 11+ languages")
    print("\nNote: Actual transcription requires valid OpenAI API key")


async def demo_intent_classification():
    """Demo: Intent Classification"""
    print("\n" + "="*60)
    print("DEMO 2: Intent Classification")
    print("="*60)
    
    classifier = IntentClassifier(
        model="gpt-4-turbo-preview",
        temperature=0.7
    )
    
    # Test with sample text
    sample_texts = [
        "Room 301 needs more towels right away",
        "What time is breakfast?",
        "The WiFi isn't working, please fix it urgently"
    ]
    
    print("\nClassifying sample transcriptions:")
    for text in sample_texts:
        print(f"\n  Input: '{text}'")
        
        # Use rule-based classification for demo (no API key needed)
        from src.intent_classifier import EntityExtractor
        entities = EntityExtractor.extract_entities(text)
        
        print(f"  Extracted Entities:")
        print(f"    - Room: {entities.get('room_number')}")
        print(f"    - Item: {entities.get('item_required')}")
        print(f"    - Quantity: {entities.get('quantity')}")
        print(f"    - Urgency: {entities.get('urgency_level')}/5")


async def demo_priority_calculation():
    """Demo: Task Priority Calculation"""
    print("\n" + "="*60)
    print("DEMO 3: Task Priority Calculation")
    print("="*60)
    
    # Test prioritizer with different scenarios
    scenarios = [
        {
            "name": "Urgent housekeeping",
            "urgency_level": 5,
            "item_required": "towels",
            "current_staff_load": 3,
            "expected": 5
        },
        {
            "name": "Routine maintenance inquiry",
            "urgency_level": 2,
            "item_required": "light bulb",
            "current_staff_load": 0,
            "expected": 2
        },
        {
            "name": "High workload + moderate urgency",
            "urgency_level": 3,
            "item_required": "coffee",
            "current_staff_load": 10,
            "expected": 3
        }
    ]
    
    print("\nPriority Calculation Scenarios:")
    for scenario in scenarios:
        priority = TaskPrioritizer.calculate_priority(
            urgency_level=scenario["urgency_level"],
            item_required=scenario["item_required"],
            current_staff_load=scenario["current_staff_load"]
        )
        
        print(f"\n  Scenario: {scenario['name']}")
        print(f"    Urgency: {scenario['urgency_level']}/5")
        print(f"    Staff Load: {scenario['current_staff_load']}/10")
        print(f"    Calculated Priority: {priority}/5")
        print(f"    [OK] Matches expected: {priority == scenario['expected']}")


async def demo_database_operations():
    """Demo: Database Operations"""
    print("\n" + "="*60)
    print("DEMO 4: Database Operations")
    print("="*60)
    
    # Initialize database
    engine = init_db()
    db = get_session(engine)
    
    try:
        # Create sample staff member
        staff = StaffMember(
            name="John Smith",
            role="Housekeeping Staff",
            department="housekeeping",
            phone_number="+1-555-0123",
            skills="cleaning,laundry,room_service",
            notification_preferences='{"push": true, "sms": false}'
        )
        
        db.add(staff)
        db.commit()
        
        print(f"\n[OK] Created staff member: {staff.name}")
        print(f"  ID: {staff.id}")
        print(f"  Department: {staff.department}")
        print(f"  Skills: {staff.skills}")
        
        # Create sample transcription
        transcription = Transcription(
            source=AudioSource.VOIP_PHONE,
            raw_text="Room 301 needs more towels and soap immediately",
            confidence_score=0.95,
            speaker_id="caller_123",
            audio_stream_id="stream_001",
            intent_type=IntentType.TASK,
            requires_human_review=False
        )
        
        db.add(transcription)
        db.commit()
        
        print(f"\n[OK] Created transcription: {transcription.id}")
        print(f"  Source: {transcription.source.value}")
        print(f"  Confidence: {transcription.confidence_score:.1%}")
        print(f"  Intent: {transcription.intent_type.value}")
        
        # Create sample task
        task = Task(
            transcription_id=transcription.id,
            description="Deliver towels and soap to room 301",
            details=transcription.raw_text,
            priority=5,
            status=TaskStatus.PENDING,
            location="Room 301",
            item_required="towels,soap",
            quantity=1,
            assigned_to=staff.id
        )
        
        db.add(task)
        db.commit()
        
        print(f"\n[OK] Created task: {task.id}")
        print(f"  Status: {task.status.value}")
        print(f"  Priority: {task.priority}/5")
        print(f"  Assigned to: {staff.name}")
        print(f"  Location: {task.location}")
        
        # Query and display
        print(f"\n[OK] Querying database...")
        
        total_tasks = db.query(Task).count()
        print(f"  Total tasks: {total_tasks}")
        
        pending_tasks = db.query(Task).filter_by(status=TaskStatus.PENDING).count()
        print(f"  Pending tasks: {pending_tasks}")
        
        staff_tasks = db.query(Task).filter_by(assigned_to=staff.id).count()
        print(f"  Assigned to {staff.name}: {staff_tasks}")
    
    finally:
        db.close()


async def demo_knowledge_base():
    """Demo: Intent Classifier Knowledge Base"""
    print("\n" + "="*60)
    print("DEMO 5: Knowledge Base Query")
    print("="*60)
    
    from src.intent_classifier import HotelKnowledgeBase
    
    kb = HotelKnowledgeBase()
    
    sample_queries = [
        "What time is breakfast?",
        "Where is the gym?",
        "How do I connect to WiFi?",
        "What's the checkout time?",
        "Is the pool open?"
    ]
    
    print("\nSample Knowledge Base Queries:")
    for query in sample_queries:
        answer, category = kb.find_answer(query)
        
        print(f"\n  Q: {query}")
        if answer:
            print(f"  A: {answer}")
            print(f"  Category: {category}")
        else:
            print(f"  A: Question not found in knowledge base")


async def demo_workflow():
    """Demo: Complete Processing Workflow"""
    print("\n" + "="*60)
    print("DEMO 6: Complete Workflow")
    print("="*60)
    
    print("\nSimulating complete audio processing flow:")
    print("\n1. Audio Input")
    print("   `-- Room 302 requesting housekeeping items")
    
    print("\n2. Transcription")
    print("   `-- 'Room 302 needs clean sheets and pillows right away'")
    
    print("\n3. Intent Classification")
    print("   `-- Intent: TASK")
    print("   `-- Urgency: HIGH (5/5)")
    print("   `-- Location: Room 302")
    
    print("\n4. Priority Calculation")
    print("   |-- Urgency weight: 40%")
    print("   |-- Inventory status: 20%")
    print("   |-- Staff workload: 20%")
    print("   `-- Priority: 5/5")
    
    print("\n5. Staff Assignment")
    print("   `-- John Smith (Housekeeping)")
    print("   `-- Available & skilled in room_service")
    
    print("\n6. Notification Dispatch")
    print("   |-- Push notification")
    print("   |-- SMS alert")
    print("   `-- Voice call (if high urgency)")
    
    print("\n7. Task Tracking")
    print("   `-- Task created, assigned, and tracked in database")


async def main():
    """Run all demos"""
    
    print("\n")
    print("+" + "-"*58 + "+")
    print("|" + " "*58 + "|")
    print("|" + "  AI Communication Engine - Demo Suite".center(58) + "|")
    print("|" + " "*58 + "|")
    print("+" + "-"*58 + "+")
    
    try:
        await demo_transcription()
        await demo_intent_classification()
        await demo_priority_calculation()
        await demo_database_operations()
        await demo_knowledge_base()
        await demo_workflow()
        
        print("\n" + "="*60)
        print("[OK] ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nTo start the full service:")
        print("  python src/AI-CommunicationEngine.py")
        print("  (or: uvicorn src.AI-CommunicationEngine:app --reload)")
        print("\n")
    
    except Exception as e:
        logger.error(f"Demo error: {str(e)}")
        print(f"\n[FAIL] Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
