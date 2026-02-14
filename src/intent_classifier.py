"""
Intent Classification Service
Classifies transcriptions into Task, Inquiry, General Chatter, or Escalation
"""

import asyncio
import logging
import json
import re
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

logger = logging.getLogger(__name__)


class IntentType(str, Enum):
    """Classification of audio intent"""
    TASK = "task"
    INQUIRY = "inquiry"
    GENERAL_CHATTER = "general_chatter"
    URGENT = "urgent"
    ESCALATION = "escalation"


class LLMProvider(str, Enum):
    """Available LLM providers for intent classification"""
    OPENAI_GPT = "openai_gpt"
    HUGGINGFACE = "huggingface"


@dataclass
class IntentClassification:
    """Container for intent classification result"""
    intent_type: IntentType
    confidence: float
    primary_intent: str
    secondary_intents: List[str]
    extracted_entities: Dict[str, Any]
    requires_human_review: bool
    reasoning: str
    suggested_priority: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_type": self.intent_type.value,
            "confidence": self.confidence,
            "primary_intent": self.primary_intent,
            "secondary_intents": self.secondary_intents,
            "extracted_entities": self.extracted_entities,
            "requires_human_review": self.requires_human_review,
            "reasoning": self.reasoning,
            "suggested_priority": self.suggested_priority,
            "timestamp": datetime.utcnow().isoformat()
        }


class EntityExtractor:
    """Extracts structured entities from text"""
    
    PATTERNS = {
        "room_number": r"room\s+(\d{3,4})|#?(\d{3,4})\b",
        "quantity": r"(\d+)\s+(towel|pillow|sheet|blanket|coffee|tea|item)?s?\b",
        "urgency": r"\b(urgent|asap|immediately|emergency|critical|now)\b",
        "person": r"(manager|housekeeper|staff|guest|resident)",
        "location": r"(lobby|front desk|kitchen|bathroom|bedroom|pool|gym)",
    }
    
    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        """Extract entities from text"""
        entities = {}
        text_lower = text.lower()
        
        for entity_type, pattern in EntityExtractor.PATTERNS.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                if matches and isinstance(matches[0], tuple):
                    matches = [m for match_tuple in matches for m in match_tuple if m]
                entities[entity_type] = list(set(matches))
        
        return entities
    
    @staticmethod
    def extract_room_number(text: str) -> Optional[str]:
        """Extract room number if present"""
        match = re.search(EntityExtractor.PATTERNS["room_number"], text, re.IGNORECASE)
        if match:
            return match.group(1) or match.group(2)
        return None
    
    @staticmethod
    def extract_quantity(text: str) -> Optional[int]:
        """Extract quantity if mentioned"""
        match = re.search(r"(\d+)\s+(?:towels|pillows|sheets|items)?", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None


class IntentClassifier:
    """Main intent classification service"""
    
    def __init__(
        self,
        provider: str = "huggingface",
        model: str = "facebook/bart-large-mnli",
        temperature: float = 0.7,
        max_tokens: int = 500,
        timeout_ms: int = 1500
    ):
        self.provider = LLMProvider(provider)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_ms / 1000
        self.entity_extractor = EntityExtractor()
        
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the LLM provider"""
        if self.provider == LLMProvider.OPENAI_GPT:
            if not HAS_OPENAI:
                raise ImportError("openai package required for GPT support")
        
        elif self.provider == LLMProvider.HUGGINGFACE:
            if not HAS_TRANSFORMERS:
                raise ImportError("transformers package required for Hugging Face support")
            # Initialize zero-shot classification pipeline
            self.hf_pipeline = pipeline(
                "zero-shot-classification",
                model=self.model
            )
        
        logger.info(f"Initialized intent classifier: {self.provider}")
    
    async def classify(
        self,
        text: str,
        speaker_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Optional[IntentClassification]:
        """
        Classify intent of transcribed text
        
        Args:
            text: Transcribed audio text
            speaker_id: Optional speaker identifier
            context: Optional context dict
            
        Returns:
            IntentClassification or None
        """
        try:
            if self.provider == LLMProvider.OPENAI_GPT:
                if not HAS_OPENAI:
                    return self._classify_with_rules(text, context)
                classification = await self._classify_with_gpt(text, speaker_id, context)
            elif self.provider == LLMProvider.HUGGINGFACE:
                if not HAS_TRANSFORMERS:
                    return self._classify_with_rules(text, context)
                classification = await self._classify_with_huggingface(text, speaker_id, context)
            else:
                classification = self._classify_with_rules(text, context)
            
            return classification
        
        except asyncio.TimeoutError:
            logger.error(f"Intent classification timeout for speaker {speaker_id}")
            return None
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return self._classify_with_rules(text, context)
    
    async def _classify_with_gpt(
        self,
        text: str,
        speaker_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Optional[IntentClassification]:
        """Classify using LLM"""
        
        system_prompt = """You are a hotel communication system. Classify the text and respond in JSON format:
{
    "intent_type": "task|inquiry|urgent|escalation|general_chatter",
    "confidence": 0.0-1.0,
    "primary_intent": "brief description",
    "secondary_intents": [],
    "room_number": "extracted room or null",
    "location": "extracted location or null",
    "item_required": "what's needed or null",
    "quantity": "quantity or null",
    "urgency_level": 1-5,
    "requires_human_review": true/false,
    "reasoning": "brief explanation",
    "suggested_priority": 1-5
}"""
        
        user_message = f"Analyze this: '{text}'\n"
        if context:
            user_message += f"Context: {json.dumps(context)}"
        
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    openai.ChatCompletion.create,
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                ),
                timeout=self.timeout_seconds
            )
            
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)
            
            llm_entities = {
                "room_number": result_json.get("room_number"),
                "location": result_json.get("location"),
                "item_required": result_json.get("item_required"),
                "quantity": result_json.get("quantity"),
            }
            
            extracted_entities = {k: v for k, v in llm_entities.items() if v is not None}
            
            classification = IntentClassification(
                intent_type=IntentType[result_json.get("intent_type", "GENERAL_CHATTER").upper()],
                confidence=float(result_json.get("confidence", 0.5)),
                primary_intent=result_json.get("primary_intent", "Unknown"),
                secondary_intents=result_json.get("secondary_intents", []),
                extracted_entities=extracted_entities,
                requires_human_review=result_json.get("requires_human_review", False),
                reasoning=result_json.get("reasoning", ""),
                suggested_priority=int(result_json.get("suggested_priority", 3))
            )
            
            logger.info(f"Classified intent: {classification.intent_type.value}")
            return classification
        
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response")
            return self._classify_with_rules(text, context)
        except asyncio.TimeoutError:
            raise
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            return self._classify_with_rules(text, context)
    
    async def _classify_with_huggingface(
        self,
        text: str,
        speaker_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Optional[IntentClassification]:
        """Classify using Hugging Face zero-shot classification"""
        try:
            # Define intent labels for zero-shot classification
            candidate_labels = [
                "task request",
                "information inquiry", 
                "urgent situation",
                "escalation request",
                "general conversation"
            ]
            
            # Run classification in a thread to avoid blocking
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    self.hf_pipeline,
                    text,
                    candidate_labels,
                    multi_class=False
                ),
                timeout=self.timeout_seconds
            )
            
            # Map top result to intent type
            top_label = result["labels"][0]
            confidence = result["scores"][0]
            
            intent_mapping = {
                "task request": IntentType.TASK,
                "information inquiry": IntentType.INQUIRY,
                "urgent situation": IntentType.URGENT,
                "escalation request": IntentType.ESCALATION,
                "general conversation": IntentType.GENERAL_CHATTER
            }
            
            intent_type = intent_mapping.get(top_label, IntentType.GENERAL_CHATTER)
            
            # Extract entities from text
            entities = self.entity_extractor.extract_entities(text)
            
            # Determine priority and review status
            requires_review = intent_type in [IntentType.URGENT, IntentType.ESCALATION]
            priority = 5 if intent_type == IntentType.URGENT else \
                      4 if intent_type == IntentType.ESCALATION else \
                      3 if intent_type == IntentType.TASK else \
                      2 if intent_type == IntentType.INQUIRY else 1
            
            classification = IntentClassification(
                intent_type=intent_type,
                confidence=float(confidence),
                primary_intent=top_label,
                secondary_intents=result["labels"][1:3] if len(result["labels"]) > 1 else [],
                extracted_entities=entities,
                requires_human_review=requires_review,
                reasoning=f"Zero-shot classification: {top_label} ({confidence:.2%})",
                suggested_priority=priority
            )
            
            logger.info(f"Classified intent (Hugging Face): {classification.intent_type.value} ({confidence:.2%})")
            return classification
        
        except asyncio.TimeoutError:
            raise
        except Exception as e:
            logger.error(f"Hugging Face classification error: {str(e)}")
            return self._classify_with_rules(text, context)
    
    def _classify_with_rules(
        self,
        text: str,
        context: Optional[Dict] = None
    ) -> IntentClassification:
        """Fallback rule-based classification"""
        text_lower = text.lower()
        
        urgent_keywords = ["emergency", "urgent", "asap", "immediately", "critical"]
        if any(keyword in text_lower for keyword in urgent_keywords):
            return IntentClassification(
                intent_type=IntentType.URGENT,
                confidence=0.85,
                primary_intent="Urgent/Emergency situation",
                secondary_intents=[],
                extracted_entities=self.entity_extractor.extract_entities(text),
                requires_human_review=True,
                reasoning="Urgent keywords detected",
                suggested_priority=5
            )
        
        escalation_keywords = ["manager", "supervisor", "owner", "escalate"]
        if any(keyword in text_lower for keyword in escalation_keywords):
            return IntentClassification(
                intent_type=IntentType.ESCALATION,
                confidence=0.8,
                primary_intent="Escalation requested",
                secondary_intents=[],
                extracted_entities=self.entity_extractor.extract_entities(text),
                requires_human_review=True,
                reasoning="Escalation keywords detected",
                suggested_priority=4
            )
        
        task_keywords = ["send", "bring", "get", "need", "clean", "fix", "replace"]
        if any(keyword in text_lower for keyword in task_keywords):
            return IntentClassification(
                intent_type=IntentType.TASK,
                confidence=0.8,
                primary_intent="Task request",
                secondary_intents=[],
                extracted_entities=self.entity_extractor.extract_entities(text),
                requires_human_review=False,
                reasoning="Task keywords detected",
                suggested_priority=3
            )
        
        inquiry_keywords = ["is", "are", "can", "when", "where", "what", "?"]
        if any(keyword in text_lower for keyword in inquiry_keywords):
            return IntentClassification(
                intent_type=IntentType.INQUIRY,
                confidence=0.75,
                primary_intent="Information request",
                secondary_intents=[],
                extracted_entities=self.entity_extractor.extract_entities(text),
                requires_human_review=False,
                reasoning="Question detected",
                suggested_priority=2
            )
        
        return IntentClassification(
            intent_type=IntentType.GENERAL_CHATTER,
            confidence=0.5,
            primary_intent="General conversation",
            secondary_intents=[],
            extracted_entities=self.entity_extractor.extract_entities(text),
            requires_human_review=False,
            reasoning="No specific intent detected",
            suggested_priority=1
        )


class HotelKnowledgeBase:
    """Hotel knowledge base for automated inquiry responses"""
    
    KNOWLEDGE_BASE = {
        "pool": {
            "is_pool_open": "The pool is open from 7:00 AM to 9:00 PM daily.",
            "pool_hours": "7:00 AM - 9:00 PM",
        },
        "wifi": {
            "password": "WiFi password is on your welcome card.",
            "connection_issues": "Unplug the router for 30 seconds and plug back in.",
        },
        "checkout": {
            "time": "Standard checkout time is 11:00 AM.",
            "late_checkout": "Late checkout available for additional fee.",
        },
        "breakfast": {
            "hours": "Breakfast served 6:30 AM - 10:00 AM in dining room.",
            "included": "Continental breakfast included with room.",
        },
        "gym": {
            "hours": "Gym is open 24/7 for hotel guests.",
            "location": "Gym is on the 2nd floor.",
        }
    }
    
    @classmethod
    def find_answer(cls, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Find answer in knowledge base"""
        query_lower = query.lower()
        
        for category, qa_pairs in cls.KNOWLEDGE_BASE.items():
            if category in query_lower:
                for key, answer in qa_pairs.items():
                    if any(word in query_lower for word in key.split("_")):
                        return answer, category
        
        return None, None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    classifier = IntentClassifier()
    
    test_texts = [
        "Room 302 needs towels immediately",
        "Is the pool open?",
        "I need to speak to a manager",
        "Emergency in the kitchen!",
    ]
    
    print("Intent Classification Examples:")
    for text in test_texts:
        result = classifier._classify_with_rules(text, None)
        print(f"\nText: {text}")
        print(f"Intent: {result.intent_type.value}")
        print(f"Priority: {result.suggested_priority}")
