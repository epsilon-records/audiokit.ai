from fastapi import APIRouter
from pydantic import BaseModel
import time
from typing import Literal
from .. import __version__

router = APIRouter()

start_time = time.time()

class HealthCheck(BaseModel):
    status: Literal["OK", "ERROR"]
    version: str
    uptime: float

@router.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    return HealthCheck(
        status="OK",
        version=__version__,
        uptime=time.time() - start_time
    ) 