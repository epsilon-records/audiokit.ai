from fastapi import APIRouter
from datetime import datetime
from audiokit_core.models.schemas import HealthCheckResponse
from ..storage.jobs import job_store

router = APIRouter()
START_TIME = datetime.utcnow()

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(
        status="ok",
        version="1.0.0",
        uptime=(datetime.utcnow() - START_TIME).total_seconds(),
        active_jobs=sum(1 for j in job_store.jobs.values() if j["status"] in ["pending", "processing"])
    ) 