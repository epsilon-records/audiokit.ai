"""Audio processing functionality for AudioKit AI."""
from typing import Dict, Any, Tuple, Optional
import logging
from pathlib import Path
import numpy as np
import librosa
from fastapi import HTTPException
from .models import ProcessingParameters

logger = logging.getLogger(__name__)

async def _load_audio(audio_data: bytes) -> Tuple[np.ndarray, int]:
    """Load audio data into memory.
    
    Args:
        audio_data: Raw audio file bytes
        
    Returns:
        Tuple of (audio_array, sample_rate)
     
    Raises:
        ValueError: If audio data is invalid
    """
    try:
        y, sr = librosa.load(audio_data)
        return y, sr
    except Exception as e:
        logger.error(f"Failed to load audio: {e}")
        raise ValueError(f"Invalid audio data: {e}")

async def analyze_audio(audio_data: bytes) -> Dict[str, Any]:
    """Analyze audio file and extract properties.
    
    Args:
        audio_data: Raw audio file bytes
        
    Returns:
        Dict containing extracted audio features
        
    Raises:
        HTTPException: If audio data is invalid or processing fails
    """
    try:
        y, sr = await _load_audio(audio_data)
        
        # Extract features
        features = {
            "duration": float(len(y) / sr),
            "sample_rate": sr,
            "peak_amplitude": float(np.max(np.abs(y))),
            "rms_level": float(np.sqrt(np.mean(y**2))),
            "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
            "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y)))
        }
        
        return features
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

async def process_audio(
    audio_data: bytes,
    params: ProcessingParameters
) -> Tuple[np.ndarray, int]:
    """Process audio with specified parameters.
    
    Args:
        audio_data: Raw audio file bytes
        params: Processing parameters
        
    Returns:
        Tuple of (processed_audio_array, sample_rate)
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        # Load audio
        y, sr = await _load_audio(audio_data)
        
        # Apply input gain
        y = y * params.input_gain
        
        # Apply effects
        for effect in params.effects:
            if effect == "normalize":
                y = librosa.util.normalize(y)
            elif effect == "trim_silence":
                y, _ = librosa.effects.trim(y)
            elif effect == "pitch_shift" and "pitch_steps" in params.model_parameters:
                y = librosa.effects.pitch_shift(
                    y, 
                    sr=sr,
                    n_steps=params.model_parameters["pitch_steps"]
                )
            elif effect == "time_stretch" and "stretch_factor" in params.model_parameters:
                y = librosa.effects.time_stretch(
                    y,
                    rate=params.model_parameters["stretch_factor"]
                )
        
        # Apply output gain
        y = y * params.output_gain
        
        # Ensure audio doesn't clip
        y = np.clip(y, -1.0, 1.0)
        
        return y, sr
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

async def save_audio(
    audio_array: np.ndarray,
    sample_rate: int,
    output_path: Path,
    format: str = "wav"
) -> None:
    """Save processed audio to file.
    
    Args:
        audio_array: Processed audio data
        sample_rate: Sample rate in Hz
        output_path: Path to save audio file
        format: Output audio format
        
    Raises:
        HTTPException: If saving fails
    """
    try:
        librosa.output.write_wav(
            str(output_path),
            audio_array,
            sample_rate
        )
    except Exception as e:
        logger.error(f"Failed to save audio: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 