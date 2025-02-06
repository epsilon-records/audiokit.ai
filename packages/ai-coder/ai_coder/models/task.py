from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

class TaskStatus(str):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DEFERRED = "DEFERRED"

class FileChange(BaseModel):
    """Represents a change to a file."""
    path: str
    content: Optional[str] = None
    diff: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None

class Task(BaseModel):
    """Represents a development task."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: int = 1
    dependencies: List[str] = []
    changes: List[FileChange] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, any] = {} 