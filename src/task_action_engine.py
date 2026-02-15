"""
Task Action Engine
Handles task creation, assignment, prioritization, and notification
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .models import (
    Task, TaskStatus, StaffMember, StaffAvailabilityStatus,
    Transcription, InventoryStatus
)

logger = logging.getLogger(__name__)


class TaskPrioritizer:
    """Determines task priority based on multiple factors"""
    
    PRIORITY_WEIGHTS = {
        "urgency": 0.40,
        "inventory_status": 0.20,
        "department_load": 0.20,
        "time_sensitivity": 0.20
    }
    
    @staticmethod
    def calculate_priority(
        urgency_level: int,
        item_required: Optional[str] = None,
        assigned_department: Optional[str] = None,
        current_staff_load: int = 0,
        db_session: Optional[Session] = None
    ) -> int:
        """Calculate priority (1-5) based on multiple factors"""
        score = 0.0
        
        # Urgency (normalized 1-5 to 0-1)
        urgency_score = min(urgency_level / 5, 1.0)
        score += urgency_score * TaskPrioritizer.PRIORITY_WEIGHTS["urgency"]
        
        # Inventory status
        inventory_score = 0.0
        if item_required and db_session:
            inventory = db_session.query(InventoryStatus).filter_by(
                item_name=item_required
            ).first()
            if inventory and not inventory.in_stock:
                inventory_score = 1.0
            elif inventory and inventory.needs_reorder:
                inventory_score = 0.7
        score += inventory_score * TaskPrioritizer.PRIORITY_WEIGHTS["inventory_status"]
        
        # Department workload
        dept_score = min(current_staff_load / 10, 1.0)
        score += (1.0 - dept_score) * TaskPrioritizer.PRIORITY_WEIGHTS["department_load"]
        
        # Time sensitivity
        time_score = 1.0 if urgency_level >= 4 else 0.3
        score += time_score * TaskPrioritizer.PRIORITY_WEIGHTS["time_sensitivity"]
        
        # Convert to 1-5 scale
        priority = max(1, min(5, int(score * 5)))
        return priority


class TaskAssigner:
    """Assigns tasks to available staff members"""
    
    @staticmethod
    async def find_best_assignee(
        department: str,
        required_skills: List[str] = None,
        location: Optional[str] = None,
        urgency_level: int = 3,
        db_session: Optional[Session] = None
    ) -> Optional[StaffMember]:
        """
        Find best staff member for task assignment
        
        Considers:
        - Availability status
        - Skills match
        - Current workload
        - Urgency level
        """
        if not db_session:
            return None
        
        query = db_session.query(StaffMember).filter(
            StaffMember.department == department,
            StaffMember.active == True
        )
        
        # High urgency: any available staff
        if urgency_level >= 4:
            available = query.filter(
                StaffMember.availability_status == StaffAvailabilityStatus.AVAILABLE
            ).all()
            if available:
                return min(available, key=lambda s: len(s.assigned_tasks))
        
        # Filter by skills if required
        if required_skills:
            eligible = []
            for staff in query.all():
                staff_skills = set(staff.skills.split(",")) if staff.skills else set()
                if any(skill in staff_skills for skill in required_skills):
                    eligible.append(staff)
        else:
            eligible = query.all()
        
        # Filter by availability
        available = [
            s for s in eligible
            if s.availability_status in [
                StaffAvailabilityStatus.AVAILABLE,
                StaffAvailabilityStatus.BUSY
            ]
        ]
        
        if not available:
            return eligible[0] if eligible else None
        
        return min(available, key=lambda s: len(s.assigned_tasks))
    
    @staticmethod
    async def assign_task(
        task: Task,
        staff_member: StaffMember,
        db_session: Session
    ) -> bool:
        """Assign task to staff member"""
        try:
            task.assigned_to = staff_member.id
            task.status = TaskStatus.PENDING
            db_session.commit()
            
            logger.info(
                f"Task {task.id} assigned to {staff_member.name} "
                f"(Priority: {task.priority})"
            )
            return True
        except Exception as e:
            logger.error(f"Error assigning task: {str(e)}")
            db_session.rollback()
            return False


class TaskActionEngine:
    """Main task action engine"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.notification_service = None
    
    async def create_task_from_transcription(
        self,
        transcription: Transcription,
        intent_classification: Dict[str, Any],
        extracted_entities: Dict[str, Any]
    ) -> Optional[Task]:
        """
        Create and assign a task from transcription and intent classification
        
        Args:
            transcription: Transcription record
            intent_classification: Result from intent classifier
            extracted_entities: Extracted entities (room, item, etc.)
            
        Returns:
            Created Task or None
        """
        try:
            # Extract task details
            room_number = extracted_entities.get("room_number")
            item_required = extracted_entities.get("item_required")
            quantity = extracted_entities.get("quantity", 1)
            urgency_level = extracted_entities.get("urgency_level", 3)
            
            # Determine department
            department = self._infer_department(item_required, room_number)
            
            # Calculate priority
            priority = TaskPrioritizer.calculate_priority(
                urgency_level=urgency_level,
                item_required=item_required,
                assigned_department=department,
                db_session=self.db_session
            )
            
            # Create task
            task = Task(
                transcription_id=transcription.id,
                description=intent_classification.get("primary_intent", ""),
                details=transcription.raw_text,
                priority=priority,
                status=TaskStatus.PENDING,
                location=room_number,
                item_required=item_required,
                quantity=quantity,
                notes=intent_classification.get("reasoning", "")
            )
            
            # Set due date based on priority
            due_offset_hours = {5: 0.5, 4: 1, 3: 4, 2: 8, 1: 24}
            task.due_date = datetime.utcnow() + timedelta(
                hours=due_offset_hours.get(priority, 4)
            )
            
            # Find assignee
            required_skills = [item_required.lower()] if item_required else []
            assignee = await TaskAssigner.find_best_assignee(
                department=department,
                required_skills=required_skills,
                location=room_number,
                urgency_level=urgency_level,
                db_session=self.db_session
            )
            
            if assignee:
                task.assigned_to = assignee.id
                logger.info(f"Task assigned to: {assignee.name}")
            
            # Save task
            self.db_session.add(task)
            self.db_session.commit()
            
            logger.info(
                f"Created task {task.id}: {task.description} "
                f"(Priority: {priority}, Location: {room_number})"
            )
            
            return task
        
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            self.db_session.rollback()
            return None
    
    async def update_task_status(
        self,
        task_id: str,
        new_status: TaskStatus,
        updated_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Update task status and create audit trail"""
        try:
            task = self.db_session.query(Task).filter_by(id=task_id).first()
            if not task:
                logger.error(f"Task {task_id} not found")
                return False
            
            old_status = task.status
            task.status = new_status
            
            if new_status == TaskStatus.COMPLETED:
                task.completed_at = datetime.utcnow()
            
            self.db_session.commit()
            logger.info(f"Task {task_id} status: {old_status} -> {new_status}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error updating task status: {str(e)}")
            self.db_session.rollback()
            return False
    
    def _infer_department(
        self,
        item_required: Optional[str] = None,
        location: Optional[str] = None
    ) -> str:
        """Infer department from item and location"""
        
        dept_keywords = {
            "housekeeping": ["towel", "sheet", "pillow", "blanket", "soap", "clean"],
            "maintenance": ["fix", "repair", "plumbing", "electrical", "light"],
            "food_beverage": ["coffee", "tea", "breakfast", "drink", "water"],
            "it": ["wifi", "internet", "phone", "tv", "connection"],
            "security": ["emergency", "suspicious", "incident", "help"],
        }
        
        item_lower = (item_required or "").lower()
        
        for dept, keywords in dept_keywords.items():
            if any(keyword in item_lower for keyword in keywords):
                return dept
        
        return "housekeeping"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Task Action Engine module loaded successfully")
