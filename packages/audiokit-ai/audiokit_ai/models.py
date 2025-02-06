"""Data models for AudioKit AI service."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
import numpy as np

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
        """Validate duration is positive."""
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v

    @validator("sample_rate")
    def sample_rate_must_be_valid(cls, v):
        """Validate sample rate is reasonable."""
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

class AudioAnalysis(BaseModel):
    """Complete audio analysis results."""
    metadata: AudioMetadata
    spectral: SpectralFeatures
    temporal: TemporalFeatures
    mfcc: Optional[List[float]] = Field(None, description="MFCC coefficients")
    additional_features: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional analysis features"
    )

    class Config:
        """Pydantic config."""
        json_encoders = {
            np.ndarray: lambda x: x.tolist(),
            np.float32: float,
            np.float64: float
        }

class ProcessingParameters(BaseModel):
    """Parameters for audio processing."""
    input_gain: float = Field(1.0, description="Input gain multiplier")
    output_gain: float = Field(1.0, description="Output gain multiplier")
    effects: List[str] = Field(default_factory=list, description="Effects to apply")
    model_parameters: dict = Field(default_factory=dict, description="ML model parameters") 