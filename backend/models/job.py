from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class JobStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

    
class JobStatus(BaseModel):
    job_id: str
    status: JobStatusEnum
    progress: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
    results: dict | None = None
    error: str | None = None