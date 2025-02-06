"""Audio processing and analysis functionality."""
import io
from pathlib import Path
from typing import Tuple, Optional
import numpy as np
import librosa
from fastapi import HTTPException
import soundfile as sf
from .models import AudioAnalysis, AudioMetadata, SpectralFeatures, TemporalFeatures
from .errors import ProcessingError
from .pipeline import ProcessingPipeline, ProcessingStage
import logging

logger = logging.getLogger(__name__)

async def load_audio(
    audio_data: bytes,
    sample_rate: Optional[int] = None
) -> Tuple[np.ndarray, int]:
    """Load audio data from bytes.
    
    Args:
        audio_data: Raw audio file bytes
        sample_rate: Optional target sample rate for resampling
        
    Returns:
        Tuple of (audio_array, sample_rate)
        
    Raises:
        ProcessingError: If audio loading fails
    """
    try:
        # Load audio using soundfile
        with io.BytesIO(audio_data) as buf:
            audio_array, sr = sf.read(buf)
            
        # Convert to mono if stereo
        if len(audio_array.shape) > 1:
            audio_array = librosa.to_mono(audio_array.T)
            
        # Resample if needed
        if sample_rate and sr != sample_rate:
            audio_array = librosa.resample(
                audio_array,
                orig_sr=sr,
                target_sr=sample_rate
            )
            sr = sample_rate
            
        return audio_array, sr
        
    except Exception as e:
        raise ProcessingError(f"Failed to load audio: {str(e)}")

async def extract_metadata(
    audio_array: np.ndarray,
    sample_rate: int,
    filename: str
) -> AudioMetadata:
    """Extract audio metadata.
    
    Args:
        audio_array: Audio signal array
        sample_rate: Sample rate in Hz
        filename: Original filename
        
    Returns:
        AudioMetadata object
    """
    return AudioMetadata(
        filename=filename,
        format=filename.split('.')[-1],
        duration=float(len(audio_array) / sample_rate),
        sample_rate=sample_rate,
        channels=1 if len(audio_array.shape) == 1 else audio_array.shape[1],
        bit_depth=audio_array.dtype.itemsize * 8
    )

async def analyze_spectral(
    audio_array: np.ndarray,
    sample_rate: int
) -> SpectralFeatures:
    """Extract spectral features.
    
    Args:
        audio_array: Audio signal array
        sample_rate: Sample rate in Hz
        
    Returns:
        SpectralFeatures object
    """
    # Calculate spectrogram
    S = np.abs(librosa.stft(audio_array))
    
    return SpectralFeatures(
        spectral_centroid=float(np.mean(
            librosa.feature.spectral_centroid(y=audio_array, sr=sample_rate)
        )),
        spectral_bandwidth=float(np.mean(
            librosa.feature.spectral_bandwidth(y=audio_array, sr=sample_rate)
        )),
        spectral_rolloff=float(np.mean(
            librosa.feature.spectral_rolloff(y=audio_array, sr=sample_rate)
        )),
        spectral_flatness=float(np.mean(
            librosa.feature.spectral_flatness(y=audio_array)
        )),
        zero_crossing_rate=float(np.mean(
            librosa.feature.zero_crossing_rate(audio_array)
        ))
    )

async def analyze_temporal(
    audio_array: np.ndarray,
    sample_rate: int
) -> TemporalFeatures:
    """Extract temporal features.
    
    Args:
        audio_array: Audio signal array
        sample_rate: Sample rate in Hz
        
    Returns:
        TemporalFeatures object
    """
    rms = np.sqrt(np.mean(audio_array**2))
    peak = np.max(np.abs(audio_array))
    
    # Estimate tempo
    onset_env = librosa.onset.onset_strength(y=audio_array, sr=sample_rate)
    tempo = float(librosa.beat.tempo(onset_envelope=onset_env, sr=sample_rate)[0])
    
    return TemporalFeatures(
        rms_energy=float(rms),
        peak_amplitude=float(peak),
        crest_factor=float(peak / rms if rms > 0 else 0),
        tempo=tempo,
        onset_rate=float(len(librosa.onset.onset_detect(
            y=audio_array,
            sr=sample_rate
        )) / (len(audio_array) / sample_rate))
    )

async def analyze_audio(
    audio_data: bytes,
    filename: str,
    sample_rate: Optional[int] = None
) -> AudioAnalysis:
    """Analyze audio file and extract features.
    
    Args:
        audio_data: Raw audio file bytes
        filename: Original filename
        sample_rate: Optional target sample rate
        
    Returns:
        AudioAnalysis object with extracted features
        
    Raises:
        ProcessingError: If analysis fails
    """
    try:
        # Load and preprocess audio
        audio_array, sr = await load_audio(audio_data, sample_rate)
        
        # Extract features
        metadata = await extract_metadata(audio_array, sr, filename)
        spectral = await analyze_spectral(audio_array, sr)
        temporal = await analyze_temporal(audio_array, sr)
        
        # Calculate MFCCs
        mfccs = librosa.feature.mfcc(y=audio_array, sr=sr, n_mfcc=13)
        mfcc_means = np.mean(mfccs, axis=1).tolist()
        
        return AudioAnalysis(
            metadata=metadata,
            spectral=spectral,
            temporal=temporal,
            mfcc=mfcc_means
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Analysis failed: {str(e)}"
        )

# Configure default pipeline stages
DEFAULT_STAGES = [
    ProcessingStage(
        name="amplitude",
        enabled=True
    ),
    ProcessingStage(
        name="spectral",
        enabled=True,
        params={
            "n_mels": 128,
            "fmax": 8000
        }
    ),
    ProcessingStage(
        name="temporal",
        enabled=True
    )
]

async def process_audio(audio_data: bytes) -> AudioAnalysis:
    """Process audio data and extract features.
    
    Args:
        audio_data: Raw audio file bytes
        
    Returns:
        Audio analysis results
        
    Raises:
        Exception: If processing fails
    """
    try:
        # Load audio file using soundfile
        with io.BytesIO(audio_data) as buf:
            y, sr = sf.read(buf)
            
        # Convert to mono if stereo
        if len(y.shape) > 1:
            y = librosa.to_mono(y.T)
            
        # Basic properties
        duration = float(len(y) / sr)
        
        # Ensure audio data is valid
        if len(y) == 0:
            raise ValueError("Empty audio data")
            
        if not np.isfinite(y).all():
            raise ValueError("Audio data contains invalid values")
            
        # Normalize audio if needed
        if np.abs(y).max() > 1.0:
            y = librosa.util.normalize(y)
            
        # Calculate features
        spectral = {}
        try:
            # Compute spectrogram
            S = np.abs(librosa.stft(y))
            
            if len(S) > 0 and np.any(S > 0):
                # Spectral features
                spectral['centroid'] = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
                spectral['bandwidth'] = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
                spectral['rolloff'] = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
            else:
                spectral['centroid'] = 0.0
                spectral['bandwidth'] = 0.0
                spectral['rolloff'] = 0.0
        except Exception as e:
            logger.warning(f"Failed to compute spectral features: {e}")
            spectral['centroid'] = 0.0
            spectral['bandwidth'] = 0.0
            spectral['rolloff'] = 0.0
            
        # Time-domain features
        temporal = {
            'duration': duration,
            'zero_crossings': int(sum(librosa.zero_crossings(y))),
            'rms': float(np.sqrt(np.mean(y**2))),
        }
        
        # Return analysis results
        return AudioAnalysis(
            sample_rate=sr,
            duration=duration,
            channels=1,
            temporal=temporal,
            spectral=spectral
        )
        
    except Exception as e:
        logger.error(f"Audio processing failed: {str(e)}", exc_info=True)
        raise Exception(f"Audio processing failed: {str(e)}")

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