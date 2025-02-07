import io
import librosa
import numpy as np
from datetime import datetime
from audiokit_core.models.schemas import ProcessingStatus, AudioFormat, AudioProcessingRequest
from .analysis import AudioAnalyzer
from .storage import JobStore
from .errors import InvalidAudioError, ProcessingError
from concurrent.futures import ProcessPoolExecutor
import asyncio
from functools import lru_cache

# Handles core audio processing logic
# Contains AudioProcessor class with DSP algorithms
# Responsible for actual audio transformations/analysis

class AudioProcessor:
    VALID_MIME_TYPES = {"audio/wav", "audio/mpeg", "audio/flac"}
    MAX_DURATION = 300  # 5 minutes
    
    def __init__(self):
        self.analyzer = AudioAnalyzer()
        self.job_store = JobStore()
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.executor = ProcessPoolExecutor(max_workers=4)
        self._init_shared_cache()
    
    def _init_shared_cache(self):
        """Cache frequently used audio processing parameters"""
        self._cache = {
            'window': np.hanning(2048),
            'mel_basis': librosa.filters.mel(sr=44100, n_fft=2048, n_mels=128)
        }

    @lru_cache(maxsize=128)
    def _load_audio(self, file_path: str) -> tuple[np.ndarray, int]:
        """Cached audio loading with memoization"""
        return librosa.load(file_path, sr=None)

    async def process(self, job_id: str, request: AudioProcessingRequest):
        """Parallel audio processing pipeline"""
        try:
            # Parallel processing stages
            raw_audio = await self.executor.submit(
                self._load_audio, request.file_path
            )
            
            processed = await asyncio.gather(
                self.executor.submit(self._apply_equalization, raw_audio),
                self.executor.submit(self._apply_compression, raw_audio),
                self.executor.submit(self._extract_features, raw_audio)
            )
            
            # Combine results
            equalized, compressed, features = processed
            final = self._mix_signals(equalized, compressed)
            
            # Store in parallel
            await asyncio.gather(
                self.executor.submit(self._store_processed_audio, job_id, final),
                self.executor.submit(self._update_metadata, job_id, features)
            )
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            raise ProcessingError(f"Processing failed: {str(e)}")

    def _validate_audio_request(self, request: AudioProcessingRequest):
        """Validate audio processing request"""
        if request.format not in AudioFormat:
            raise InvalidAudioError(f"Invalid format {request.format}")
            
        if len(request.audio_data) > self.max_file_size:
            raise InvalidAudioError("File size exceeds limit")
            
        # Validate sample rate constraints
        if not 8000 <= request.sample_rate <= 192000:
            raise InvalidAudioError("Invalid sample rate")

    def _apply_processing_pipeline(self, audio: np.ndarray, sr: int, parameters: dict) -> np.ndarray:
        """Apply processing pipeline to audio"""
        try:
            # Noise reduction
            audio = self._apply_noise_reduction(audio, sr)
            
            # Normalization
            audio = self._normalize_audio(audio)
            
            # Apply effects based on parameters
            if parameters.get("equalize", False):
                audio = self._apply_equalization(audio, sr)
                
            if parameters.get("compress", False):
                audio = self._apply_compression(audio, sr)
                
            return audio
            
        except Exception as e:
            raise ProcessingError(f"Processing pipeline failed: {str(e)}")

    def _apply_noise_reduction(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply basic noise reduction"""
        # Implementation using spectral gating
        S = np.abs(librosa.stft(audio))
        mask = librosa.util.softmask(S, S * 0.5, power=2)
        return librosa.istft(S * mask)

    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to -1dB peak"""
        peak = np.max(np.abs(audio))
        return audio * (0.99 / peak)

    def _apply_equalization(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply basic equalization"""
        # Implementation using librosa's IIR filter
        return librosa.effects.preemphasis(audio)

    def _apply_compression(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply basic dynamic range compression"""
        # Simple compression implementation
        threshold = 0.1
        ratio = 4.0
        compressed = np.where(
            np.abs(audio) > threshold,
            threshold + (np.abs(audio) - threshold) / ratio,
            audio
        )
        return np.sign(audio) * compressed

    def _store_processed_audio(self, job_id: str, audio: np.ndarray, sr: int, format: AudioFormat):
        """Store processed audio in storage system"""
        try:
            # Convert to target format
            if format == AudioFormat.WAV:
                import soundfile as sf
                sf.write(f"processed/{job_id}.wav", audio, sr)
            elif format == AudioFormat.MP3:
                import pydub
                audio_segment = pydub.AudioSegment(
                    audio.tobytes(),
                    frame_rate=sr,
                    sample_width=audio.dtype.itemsize,
                    channels=1
                )
                audio_segment.export(f"processed/{job_id}.mp3", format="mp3")
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            raise ProcessingError(f"Failed to store processed audio: {str(e)}")

    def _mix_signals(self, *signals):
        """Vectorized signal mixing"""
        return np.mean(np.array(signals), axis=0) 