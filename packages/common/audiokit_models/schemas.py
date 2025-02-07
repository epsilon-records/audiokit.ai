from pydantic import BaseModel
from typing import List

class AudioAnalysis(BaseModel):
    """Analysis results from audio processing"""
    duration: float
    sample_rate: int
    channels: int
    format: str
    features: List[float]
    metadata: dict

class HealthCheck(BaseModel):
    status: str
    version: str
    uptime: float 