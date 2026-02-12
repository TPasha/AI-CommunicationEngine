"""
Database models for AI Communication Engine
Defines schemas for transcriptions, tasks, inventory, and staff management
"""

from datetime import datetime
from typing import Optional
from enum import Enum
import uuid

from sqlalchemy import (
    create_engine, Column, String, Integer, DateTime, 
    Float, Boolean, ForeignKey, Text, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class IntentType(str, Enum):
    """Classification of audio intent"""
    TASK = "task"
    INQUIRY = "inquiry"
    GENERAL_CHATTER = "general_chatter"
    URGENT = "urgent"
    ESCALATION = "escalation"


class TaskStatus(str, Enum):
    """Task lifecycle states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class StaffAvailabilityStatus(str, Enum):
    """Staff member availability"""
    AVAILABLE = "available"
    BUSY = "busy"
    ON_BREAK = "on_break"
    OFF_DUTY = "off_duty"


class AudioSource(str, Enum):
    """Source of audio stream"""
    WALKIE_TALKIE = "walkie_talkie"
    VOIP_PHONE = "voip_phone"
    DIRECT_CALL = "direct_call"


class Transcription(Base):
    """Stores raw transcriptions from audio streams"""
    __tablename__ = "transcriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(SQLEnum(AudioSource), nullable=False)
    raw_text = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.0)
    speaker_id = Column(String(255), nullable=True)
    speaker_name = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    audio_stream_id = Column(String(36), nullable=False)
    
    intent_type = Column(SQLEnum(IntentType), nullable=True)
    intent_confidence = Column(Float, default=0.0)
    requires_human_review = Column(Boolean, default=False)
    
    task = relationship("Task", back_populates="transcription", uselist=False)
    inquiry_response = relationship("InquiryResponse", back_populates="transcription", uselist=False)
    
    def __repr__(self):
        return f"<Transcription(id={self.id}, source={self.source})>"


class Task(Base):
    """Represents actionable tasks extracted from audio"""
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transcription_id = Column(String(36), ForeignKey("transcriptions.id"), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    priority = Column(Integer, default=3, nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    assigned_to = Column(String(36), ForeignKey("staff_members.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    location = Column(String(255), nullable=True)
    item_required = Column(String(255), nullable=True)
    quantity = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    transcription = relationship("Transcription", back_populates="task")
    assigned_staff = relationship("StaffMember", back_populates="assigned_tasks")
    status_updates = relationship("TaskStatusUpdate", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id={self.id}, priority={self.priority})>"


class TaskStatusUpdate(Base):
    """Audit trail for task status changes"""
    __tablename__ = "task_status_updates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    old_status = Column(SQLEnum(TaskStatus), nullable=False)
    new_status = Column(SQLEnum(TaskStatus), nullable=False)
    updated_by = Column(String(36), ForeignKey("staff_members.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
    
    task = relationship("Task", back_populates="status_updates")
    
    def __repr__(self):
        return f"<TaskStatusUpdate(task_id={self.task_id})>"


class InquiryResponse(Base):
    """Handles automated responses to inquiries"""
    __tablename__ = "inquiry_responses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transcription_id = Column(String(36), ForeignKey("transcriptions.id"), nullable=False)
    query_text = Column(Text, nullable=False)
    knowledge_base_category = Column(String(255), nullable=True)
    response_text = Column(Text, nullable=False)
    response_method = Column(String(50), default="voice_and_text")
    confidence_score = Column(Float, default=0.0)
    human_review_required = Column(Boolean, default=False)
    responded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    transcription = relationship("Transcription", back_populates="inquiry_response")
    
    def __repr__(self):
        return f"<InquiryResponse(id={self.id})>"


class StaffMember(Base):
    """Staff member profiles and availability tracking"""
    __tablename__ = "staff_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    device_token = Column(String(500), nullable=True)
    
    availability_status = Column(SQLEnum(StaffAvailabilityStatus), default=StaffAvailabilityStatus.AVAILABLE)
    last_status_update = Column(DateTime, default=datetime.utcnow)
    skills = Column(String(500), nullable=True)
    notification_preferences = Column(String(500), nullable=True)
    preferred_languages = Column(String(255), default="en")
    
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    assigned_tasks = relationship("Task", back_populates="assigned_staff")
    
    def __repr__(self):
        return f"<StaffMember(id={self.id}, name={self.name})>"


class InventoryStatus(Base):
    """Real-time inventory tracking"""
    __tablename__ = "inventory_status"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    quantity_available = Column(Integer, default=0)
    quantity_total = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    reorder_level = Column(Integer, default=5)
    
    in_stock = Column(Boolean, default=True)
    needs_reorder = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<InventoryStatus(id={self.id}, item={self.item_name})>"


class AudioStreamSession(Base):
    """Represents a single audio stream session"""
    __tablename__ = "audio_stream_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(SQLEnum(AudioSource), nullable=False)
    stream_key = Column(String(255), nullable=False, unique=True)
    caller_id = Column(String(255), nullable=True)
    caller_name = Column(String(255), nullable=True)
    
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    status = Column(String(50), default="active")
    packet_loss_percent = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<AudioStreamSession(id={self.id}, source={self.source})>"


def init_db(database_url: str = "sqlite:///communication_engine.db"):
    """Initialize the database with all tables"""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get a database session"""
    Session = sessionmaker(bind=engine)
    return Session()
