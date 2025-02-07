from datetime import datetime
from uuid import uuid4
from typing import Dict
from audiokit_core.models.schemas import ProcessedAudioResponse, ProcessingStatus

class JobStore:
    def __init__(self):
        self.jobs: Dict[str, dict] = {}

    def create_job(self):
        job_id = str(uuid4())
        job = {
            "id": job_id,
            "status": ProcessingStatus.PENDING,
            "created_at": datetime.utcnow(),
            "completed_at": None,
            "duration": None,
            "format": None,
            "error": None
        }
        self.jobs[job_id] = job
        return Job(**job)

    def get_job(self, job_id: str):
        job = self.jobs.get(job_id)
        return Job(**job) if job else None

    def update_job(self, job_id: str, **kwargs):
        if job_id in self.jobs:
            self.jobs[job_id].update(kwargs)

class Job:
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.status = kwargs["status"]
        self.created_at = kwargs["created_at"]
        self.completed_at = kwargs["completed_at"]
        self.duration = kwargs["duration"]
        self.format = kwargs["format"]
        self.error = kwargs["error"]

    def to_response(self):
        return ProcessedAudioResponse(
            job_id=self.id,
            status=self.status,
            created_at=self.created_at,
            completed_at=self.completed_at,
            duration=self.duration,
            format=self.format,
            error=self.error
        ) 