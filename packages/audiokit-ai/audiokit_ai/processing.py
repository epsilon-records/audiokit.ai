"""Audio processing and analysis functionality."""
import io
from typing import Tuple, Optional
import numpy as np
import librosa
from fastapi import HTTPException
import soundfile as sf
from .models import AudioAnalysis, AudioMetadata, SpectralFeatures, TemporalFeatures
from .errors import ProcessingError

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