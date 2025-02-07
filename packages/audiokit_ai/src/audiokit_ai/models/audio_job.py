from pydantic import BaseModel
from datetime import datetime

class AudioJob(BaseModel):
    id: int
    task_name: str
    status: str
    created_at: datetime
    result_url: str = None 