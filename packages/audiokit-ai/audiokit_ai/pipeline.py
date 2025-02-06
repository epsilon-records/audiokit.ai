"""Audio processing pipeline implementation."""
from typing import Optional, List, Dict, Any
from pathlib import Path
import tempfile
import asyncio
import soundfile as sf
import librosa
import numpy as np
from pydantic import BaseModel

from .models import AudioAnalysis
from .errors import ProcessingError

class ProcessingStage(BaseModel):
    """Base model for processing stage configuration."""
    name: str
    enabled: bool = True
    params: Dict[str, Any] = {}

class ProcessingPipeline:
    """Audio processing pipeline manager."""
    
    def __init__(self):
        self.stages: List[ProcessingStage] = []
        self._temp_dir = Path(tempfile.mkdtemp(prefix="audiokit-"))
        
    async def process(self, audio_data: bytes) -> AudioAnalysis:
        """Process audio through pipeline stages.
        
        Args:
            audio_data: Raw audio file bytes
            
        Returns:
            Audio analysis results
            
        Raises:
            ProcessingError: If processing fails
        """
        try:
            # Load audio
            y, sr = self._load_audio(audio_data)
            
            # Initialize results
            results = {
                "duration": float(len(y) / sr),
                "sample_rate": sr,
                "channels": 1 if len(y.shape) == 1 else y.shape[1]
            }
            
            # Run enabled stages
            for stage in self.stages:
                if stage.enabled:
                    stage_results = await self._run_stage(stage, y, sr)
                    results.update(stage_results)
            
            return AudioAnalysis(**results)
            
        except Exception as e:
            raise ProcessingError(f"Pipeline processing failed: {str(e)}")
        
    def _load_audio(self, audio_data: bytes) -> tuple[np.ndarray, int]:
        """Load audio data into numpy array.
        
        Args:
            audio_data: Raw audio file bytes
            
        Returns:
            Tuple of (audio_array, sample_rate)
            
        Raises:
            ProcessingError: If loading fails
        """
        try:
            # Write bytes to temporary file
            temp_path = self._temp_dir / "temp_audio"
            temp_path.write_bytes(audio_data)
            
            # Load with soundfile
            y, sr = sf.read(temp_path)
            
            # Convert to mono if stereo
            if len(y.shape) > 1:
                y = librosa.to_mono(y.T)
                
            return y, sr
            
        except Exception as e:
            raise ProcessingError(f"Failed to load audio: {str(e)}")
            
    async def _run_stage(
        self,
        stage: ProcessingStage,
        y: np.ndarray,
        sr: int
    ) -> Dict[str, Any]:
        """Run single processing stage.
        
        Args:
            stage: Processing stage to run
            y: Audio array
            sr: Sample rate
            
        Returns:
            Stage processing results
            
        Raises:
            ProcessingError: If stage processing fails
        """
        try:
            # Run CPU-intensive processing in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self._process_stage,
                stage,
                y,
                sr
            )
            
        except Exception as e:
            raise ProcessingError(
                f"Stage {stage.name} failed: {str(e)}"
            )
            
    def _process_stage(
        self,
        stage: ProcessingStage,
        y: np.ndarray,
        sr: int
    ) -> Dict[str, Any]:
        """Execute stage processing (CPU-intensive).
        
        Args:
            stage: Processing stage to run
            y: Audio array
            sr: Sample rate
            
        Returns:
            Stage results
        """
        if stage.name == "amplitude":
            return {
                "peak_amplitude": float(np.max(np.abs(y))),
                "rms_level": float(np.sqrt(np.mean(y**2)))
            }
            
        elif stage.name == "spectral":
            # Compute mel spectrogram
            S = librosa.feature.melspectrogram(
                y=y,
                sr=sr,
                **stage.params
            )
            
            return {
                "spectral_centroid": float(np.mean(
                    librosa.feature.spectral_centroid(S=librosa.power_to_db(S))
                )),
                "spectral_bandwidth": float(np.mean(
                    librosa.feature.spectral_bandwidth(S=librosa.power_to_db(S))
                ))
            }
            
        elif stage.name == "temporal":
            return {
                "tempo": float(librosa.beat.tempo(y=y, sr=sr)[0]),
                "zero_crossing_rate": float(np.mean(
                    librosa.feature.zero_crossing_rate(y)
                ))
            }
            
        return {} 