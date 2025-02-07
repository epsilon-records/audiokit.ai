from fastapi import APIRouter, File, UploadFile, Query
import librosa
import numpy as np
import io
from typing import List
from fastapi import HTTPException

router = APIRouter()

@router.post("/api/v1/analyze/loudness")
async def analyze_loudness(
    audio_file: UploadFile = File(...),
    window_size: float = 0.1  # 100ms analysis windows
):
    audio_data = await audio_file.read()
    
    # Librosa analysis
    y, sr = librosa.load(io.BytesIO(audio_data), sr=None)
    S = np.abs(librosa.stft(y))
    loudness = librosa.amplitude_to_db(S, ref=np.max)
    
    # Temporal averaging
    frame_length = int(window_size * sr)
    loudness_curve = librosa.util.frame(
        loudness.mean(axis=0),
        frame_length=frame_length,
        hop_length=frame_length
    ).mean(axis=0)
    
    return {
        "loudness": loudness_curve.tolist(),
        "sample_rate": sr,
        "window_size": window_size
    }

@router.post("/api/v1/analyze/spectral")
async def spectral_analysis(
    audio_file: UploadFile = File(...),
    features: List[str] = Query(["mfcc", "centroid", "bandwidth", "contrast", "rolloff"])
):
    """Comprehensive spectral analysis endpoint"""
    try:
        y, sr = librosa.load(io.BytesIO(await audio_file.read()), sr=None)
        
        analysis = {}
        if "mfcc" in features:
            analysis["mfcc"] = librosa.feature.mfcc(y=y, sr=sr).tolist()
        if "centroid" in features:
            analysis["centroid"] = librosa.feature.spectral_centroid(y=y, sr=sr).tolist()
        if "bandwidth" in features:
            analysis["bandwidth"] = librosa.feature.spectral_bandwidth(y=y, sr=sr).tolist()
        if "contrast" in features:
            analysis["contrast"] = librosa.feature.spectral_contrast(y=y, sr=sr).tolist()
        if "rolloff" in features:
            analysis["rolloff"] = librosa.feature.spectral_rolloff(y=y, sr=sr).tolist()
            
        return {
            "status": "success",
            "analysis": analysis,
            "duration": librosa.get_duration(y=y, sr=sr),
            "sample_rate": sr
        }
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")

@router.post("/api/v1/analyze/bpm")
async def analyze_bpm(
    audio_file: UploadFile = File(...),
    method: str = Query("librosa", enum=["librosa", "madmom"])
):
    """Estimate audio tempo (BPM)"""
    try:
        y, sr = librosa.load(io.BytesIO(await audio_file.read()), sr=None)
        
        if method == "madmom":
            from madmom.features.tempo import TempoEstimationProcessor
            proc = TempoEstimationProcessor(fps=100)
            tempo = proc(y)
            bpm = float(tempo[0])
        else:
            bpm = float(librosa.beat.tempo(y=y, sr=sr)[0])
            
        return {
            "status": "success",
            "bpm": bpm,
            "method": method,
            "duration": librosa.get_duration(y=y, sr=sr)
        }
    except Exception as e:
        raise HTTPException(500, f"BPM analysis failed: {str(e)}") 