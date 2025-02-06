"""Data models for AudioKit AI service."""
from typing import Optional, List
from pydantic import BaseModel, Field

class AudioAnalysis(BaseModel):
    """Results of audio file analysis."""
    duration: float = Field(..., description="Duration in seconds")
    sample_rate: int = Field(..., description="Sample rate in Hz")
    channels: int = Field(..., description="Number of audio channels")
    format: str = Field(..., description="Audio format")
    bit_depth: Optional[int] = Field(None, description="Bit depth")
    
    # Analysis results
    peak_amplitude: float = Field(..., description="Peak amplitude")
    rms_level: float = Field(..., description="RMS level")
    spectral_centroid: float = Field(..., description="Spectral centroid")
    tempo: Optional[float] = Field(None, description="Detected tempo in BPM")
    
    # Feature extraction
    mfcc: Optional[List[float]] = Field(None, description="MFCC coefficients")
    spectral_rolloff: Optional[float] = Field(None, description="Spectral rolloff")
    zero_crossing_rate: Optional[float] = Field(None, description="Zero crossing rate")

class ProcessingParameters(BaseModel):
    """Parameters for audio processing."""
    input_gain: float = Field(1.0, description="Input gain multiplier")
    output_gain: float = Field(1.0, description="Output gain multiplier")
    effects: List[str] = Field(default_factory=list, description="Effects to apply")
    model_parameters: dict = Field(default_factory=dict, description="ML model parameters") 