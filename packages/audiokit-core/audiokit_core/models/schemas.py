from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AudioFormat(str, Enum):
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"

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

class AudioProcessingRequest(BaseModel):
    """Request schema for audio processing"""
    audio_data: bytes = Field(..., description="Raw audio bytes")
    format: AudioFormat = Field(..., description="Audio format specification")
    sample_rate: int = Field(44100, description="Sample rate in Hz")
    parameters: dict = Field({}, description="Processing parameters")

class ProcessedAudioResponse(BaseModel):
    """Response schema for processed audio"""
    job_id: str = Field(..., description="Unique processing job ID")
    status: ProcessingStatus = Field(..., description="Current job status")
    processed_data: Optional[bytes] = Field(None, description="Processed audio bytes")
    format: Optional[AudioFormat] = Field(None, description="Output audio format")
    duration: Optional[float] = Field(None, description="Processed audio duration in seconds")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    error: Optional[str] = Field(None, description="Error message if processing failed")

class AudioMetadata(BaseModel):
    """Audio file metadata."""
    filename: str = Field(..., description="Original filename")
    format: str = Field(..., description="Audio format (wav, mp3, etc)")
    duration: float = Field(..., description="Duration in seconds")
    sample_rate: int = Field(..., description="Sample rate in Hz")
    channels: int = Field(..., description="Number of audio channels")
    bit_depth: Optional[int] = Field(None, description="Bit depth if applicable")

    @validator("duration")
    def duration_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v

    @validator("sample_rate")
    def sample_rate_must_be_valid(cls, v):
        if not 8000 <= v <= 192000:
            raise ValueError("Sample rate must be between 8kHz and 192kHz")
        return v

class SpectralFeatures(BaseModel):
    """Spectral analysis features."""
    spectral_centroid: float = Field(..., description="Spectral centroid in Hz")
    spectral_bandwidth: float = Field(..., description="Spectral bandwidth")
    spectral_rolloff: float = Field(..., description="Spectral rolloff frequency")
    spectral_flatness: float = Field(..., description="Spectral flatness")
    zero_crossing_rate: float = Field(..., description="Zero crossing rate")

class TemporalFeatures(BaseModel):
    """Temporal analysis features."""
    rms_energy: float = Field(..., description="RMS energy")
    peak_amplitude: float = Field(..., description="Peak amplitude")
    crest_factor: float = Field(..., description="Crest factor (peak/RMS)")
    tempo: Optional[float] = Field(None, description="Estimated tempo in BPM")
    onset_rate: Optional[float] = Field(None, description="Onset rate")

class AnalysisResult(BaseModel):
    """Enhanced analysis results with validation"""
    sample_rate: Optional[int] = None
    duration: Optional[float] = None
    channels: Optional[int] = None
    spectral: Dict[str, float] = {}
    temporal: Dict[str, Any] = {}
    tempo: Optional[float] = None
    mfcc_features: Optional[List[float]] = None
    errors: List[str] = []

    # Add relationship to processing request
    parameters: Optional[Dict[str, Any]] = Field(
        None, 
        description="Processing parameters used"
    )

class HealthCheckResponse(BaseModel):
    status: str = Field(..., example="ok", description="Service health status")
    version: str = Field(..., example="1.0.0", description="API version")
    uptime: float = Field(..., example=1234.56, description="Service uptime in seconds")
    active_jobs: int = Field(..., example=5, description="Number of currently processing jobs")

class ErrorResponse(BaseModel):
    error_type: str = Field(..., description="Error category")
    detail: str = Field(..., description="Human-readable error description")
    context: Optional[dict] = Field(None, description="Additional error context")

class ProcessingParameters(BaseModel):
    """Parameters for audio processing."""
    input_gain: float = Field(1.0, description="Input gain multiplier")
    output_gain: float = Field(1.0, description="Output gain multiplier")
    effects: List[str] = Field(default_factory=list, description="Effects to apply")
    model_parameters: dict = Field(
        default_factory=dict, 
        description="ML model parameters"
    ) 