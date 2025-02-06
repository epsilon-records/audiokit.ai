"""Audio processing and analysis functionality."""
import io
from pathlib import Path
from typing import Tuple, Optional, Dict
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
    
    # Estimate tempo using old function location
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

def estimate_key(y: np.ndarray, sr: int) -> str:
    """Estimate musical key of audio."""
    # Compute chromagram
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    
    # Key detection using template matching
    key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    major_template = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
    minor_template = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
    
    # Average chroma over time
    chroma_avg = np.mean(chroma, axis=1)
    
    # Correlate with templates
    major_corr = np.correlate(chroma_avg, major_template, mode='full')
    minor_corr = np.correlate(chroma_avg, minor_template, mode='full')
    
    # Find best match
    if np.max(major_corr) > np.max(minor_corr):
        key_idx = np.argmax(major_corr) % 12
        mode = "major"
    else:
        key_idx = np.argmax(minor_corr) % 12
        mode = "minor"
        
    return f"{key_names[key_idx]} {mode}"

def compute_energy(y: np.ndarray) -> float:
    """Compute energy level of audio."""
    # Combine RMS energy and spectral energy
    rms = librosa.feature.rms(y=y)[0]
    spectral = np.abs(librosa.stft(y))
    
    # Normalize and combine
    rms_energy = np.mean(rms) / np.max(rms) if np.max(rms) > 0 else 0
    spectral_energy = np.mean(spectral) / np.max(spectral) if np.max(spectral) > 0 else 0
    
    return float(0.5 * (rms_energy + spectral_energy))

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
        
        # Compute tempo (BPM)
        tempo = None
        try:
            onset_env = librosa.onset.onset_strength(y=audio_array, sr=sr)
            tempo = float(librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0])
        except Exception as e:
            logger.warning(f"Failed to compute tempo: {e}")
            
        # Estimate musical key
        key = None
        try:
            key = estimate_key(audio_array, sr)
        except Exception as e:
            logger.warning(f"Failed to estimate key: {e}")
            
        # Compute energy level
        energy = None
        try:
            energy = compute_energy(audio_array)
        except Exception as e:
            logger.warning(f"Failed to compute energy: {e}")
            
        # Compute harmonic/percussive separation
        harmonic_percussive = None
        try:
            y_harmonic, y_percussive = librosa.effects.hpss(audio_array)
            harmonic_percussive = {
                'harmonic_ratio': float(np.mean(np.abs(y_harmonic)) / np.mean(np.abs(audio_array))),
                'percussive_ratio': float(np.mean(np.abs(y_percussive)) / np.mean(np.abs(audio_array)))
            }
        except Exception as e:
            logger.warning(f"Failed to compute harmonic/percussive separation: {e}")
        
        return AudioAnalysis(
            metadata=metadata,
            spectral=spectral,
            temporal=temporal,
            mfcc=mfcc_means,
            tempo=tempo,
            key=key,
            energy=energy,
            harmonic_percussive=harmonic_percussive
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
    results = {
        'sample_rate': None,
        'duration': None,
        'channels': None,
        'spectral': {},
        'temporal': {},
        'errors': []  # Track any errors during processing
    }
    
    try:
        # Load audio file using soundfile
        try:
            with io.BytesIO(audio_data) as buf:
                y, sr = sf.read(buf)
                
            # Convert to mono if stereo
            if len(y.shape) > 1:
                y = librosa.to_mono(y.T)
                
            results['sample_rate'] = sr
            results['duration'] = float(len(y) / sr)
            results['channels'] = 1 if len(y.shape) == 1 else y.shape[1]
            
            # Ensure audio data is valid
            if len(y) == 0:
                raise ValueError("Empty audio data")
                
            if not np.isfinite(y).all():
                raise ValueError("Audio data contains invalid values")
                
            # Normalize audio if needed
            if np.abs(y).max() > 1.0:
                y = librosa.util.normalize(y)
                
        except Exception as e:
            logger.error(f"Failed to load audio: {e}")
            results['errors'].append(f"Audio loading failed: {str(e)}")
            return AudioAnalysis(**results)
            
        # Calculate spectral features
        try:
            S = np.abs(librosa.stft(y))
            if len(S) > 0 and np.any(S > 0):
                results['spectral'].update({
                    'centroid': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                    'bandwidth': float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))),
                    'rolloff': float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))),
                    'flatness': float(np.mean(librosa.feature.spectral_flatness(y=y)))
                })
        except Exception as e:
            logger.warning(f"Failed to compute spectral features: {e}")
            results['errors'].append(f"Spectral analysis failed: {str(e)}")
            results['spectral'].update({
                'centroid': 0.0,
                'bandwidth': 0.0,
                'rolloff': 0.0,
                'flatness': 0.0
            })
            
        # Calculate temporal features
        try:
            results['temporal'].update({
                'duration': results['duration'],
                'zero_crossings': int(sum(librosa.zero_crossings(y))),
                'rms': float(np.sqrt(np.mean(y**2))),
            })
        except Exception as e:
            logger.warning(f"Failed to compute temporal features: {e}")
            results['errors'].append(f"Temporal analysis failed: {str(e)}")
            
        # Compute tempo (BPM)
        try:
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            results['tempo'] = float(librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0])
        except Exception as e:
            logger.warning(f"Failed to compute tempo: {e}")
            results['errors'].append(f"Tempo detection failed: {str(e)}")
            results['tempo'] = None
            
        # Compute MFCCs
        try:
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            results['mfcc_features'] = np.mean(mfccs, axis=1).tolist()
        except Exception as e:
            logger.warning(f"Failed to compute MFCCs: {e}")
            results['errors'].append(f"MFCC computation failed: {str(e)}")
            results['mfcc_features'] = None
            
        # Return analysis results even if some computations failed
        return AudioAnalysis(**results)
        
    except Exception as e:
        logger.error(f"Audio processing failed: {str(e)}", exc_info=True)
        results['errors'].append(f"Processing failed: {str(e)}")
        return AudioAnalysis(**results)

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