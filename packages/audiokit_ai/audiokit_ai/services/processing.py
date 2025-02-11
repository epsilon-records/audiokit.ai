# CONFIDENTIAL AND PROPRIETARY
#
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
#
# This software is confidential and proprietary.
#

#
# This file is part of the AudioKit AI package.
#

import asyncio
import base64
import hashlib
import io
import json
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

import faiss
import matchering as mg
import numpy as np
import openl3
import soundfile as sf
import torch
import torchaudio
import whisper
from demucs import separate
from demucs.apply import apply_model
from demucs.pretrained import get_model
from df import enhance, init_df
from fastapi import HTTPException, UploadFile
from google.cloud import speech_v1p1beta1 as speech

from audiokit_ai.core.logger import logger


# Initialize DeepFilterNet using the recommended API
model, df_state, _ = init_df()
whisper_model = whisper.load_model("base")

# Initialize FAISS index and OpenL3 model
index = faiss.IndexFlatL2(512)
openl3_model = openl3.models.load_audio_embedding_model(
    input_repr="mel256",  # Mel-spectrogram with 256 bins
    content_type="music",  # Use "music" for music-related tasks
    embedding_size=512,  # Size of the embedding vector
)

# Initialize the SpeechClient
try:
    # Get the path to the credentials file from environment
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")

    # Verify the file exists
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")

    # Read and parse the credentials file
    with open(credentials_path) as f:
        credentials = json.load(f)

    # Initialize the SpeechClient
    speech_client = speech.SpeechClient.from_service_account_info(credentials)
    logger.info("Successfully initialized SpeechClient")

except json.JSONDecodeError as e:
    logger.error(f"Failed to parse credentials JSON: {e!s}")
    raise RuntimeError("Invalid credentials file format")
except Exception as e:
    logger.error(f"Failed to initialize SpeechClient: {e!s}")
    raise RuntimeError(f"Failed to initialize SpeechClient: {e!s}")


async def save_temp_file(file: UploadFile) -> str:
    """Save an uploaded file to a temporary location"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            # Write the uploaded file's content to the temp file
            temp_file.write(await file.read())
            logger.info(f"Saved temporary file: {temp_file.name}")
            return temp_file.name
    except Exception as e:
        logger.error(f"Failed to save temporary file: {e!s}")
        raise RuntimeError(f"Failed to save temporary file: {e!s}")


def get_tensorflow():
    import tensorflow as tf

    # Prevent fragmentation and limit GPU memory growth
    tf.config.set_visible_devices([], "GPU")
    tf.config.optimizer.set_jit(True)  # Enable XLA
    return tf


class ProcessingState:
    def __init__(self):
        self._progress = 0
        self._lock = asyncio.Lock()  # Add lock for thread safety

    async def set_progress(self, value: float):
        """Set the current progress value."""
        async with self._lock:
            self._progress = value
            logger.debug(f"Progress updated to: {value}%")

    def get_progress(self) -> float:
        """Get the current progress value."""
        return self._progress


processing_state = ProcessingState()


def get_progress():
    """Get the current processing progress."""
    return processing_state.get_progress()


async def denoise_speech(file: UploadFile, progress_callback: callable = None) -> dict:
    """Reduce noise in speech/vocal audio using DeepFilterNet"""
    try:
        # Save the uploaded file temporarily
        temp_path = await save_temp_file(file)

        # Get audio info
        info = sf.info(temp_path)
        total_frames = info.frames
        chunk_size = 1024 * 1024  # 1MB chunks

        # Calculate number of chunks for accurate progress
        num_chunks = (total_frames + chunk_size - 1) // chunk_size

        # Process in chunks
        processed_chunks = []
        with sf.SoundFile(temp_path) as infile:
            for i, chunk in enumerate(infile.blocks(chunk_size)):
                # Process chunk
                audio_tensor = torch.from_numpy(chunk).float()
                if len(audio_tensor.shape) == 1:
                    audio_tensor = audio_tensor.unsqueeze(0)
                processed = enhance(model, df_state, audio_tensor)
                processed_chunks.append(processed.squeeze().numpy())

                # Update progress (ensure it doesn't exceed 100%)
                if progress_callback:
                    progress = min(int((i + 1) * 100 / num_chunks), 100)
                    await progress_callback(progress)
                    logger.info(f"Processing progress: {progress}%")

                # Clean up
                del audio_tensor
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

        # Combine processed chunks
        processed_audio = np.concatenate(processed_chunks)

        # Send 100% progress before saving
        if progress_callback:
            await progress_callback(100)
            logger.info("Processing complete: 100%")

        # Save result to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            sf.write(temp_file.name, processed_audio, info.samplerate)
            logger.info(f"Saved processed file: {temp_file.name}")

        return {"status": "success", "file_path": temp_file.name}
    except Exception as e:
        logger.error(f"Error during speech denoising: {e}")
        raise RuntimeError(f"Speech denoising failed: {e}")


async def separate_stems(file: UploadFile) -> dict:
    """Separate audio into stems using Demucs"""
    try:
        # Save the uploaded file temporarily
        audio_path = await save_temp_file(file)

        # Separate audio into stems
        stems = separate(audio_path)

        # Load each stem as bytes
        result = {}
        for stem, stem_path in stems.items():
            with open(stem_path, "rb") as f:
                result[stem] = f.read()

        return result
    except Exception as e:
        raise RuntimeError(f"Audio separation failed: {e!s}")


async def auto_master(file: UploadFile, reference_file: UploadFile) -> str:
    """
    Apply automatic mastering to an audio file using Matchering.

    Args:
        file: The audio file to master.
        reference_file: The reference audio file to match.

    Returns:
        Base64-encoded WAV audio data of the mastered signal.
    """
    try:
        # Load the target and reference audio
        target_data = await file.read()
        reference_data = await reference_file.read()

        # Load audio files into NumPy arrays
        target_audio, target_sr = sf.read(io.BytesIO(target_data))
        reference_audio, reference_sr = sf.read(io.BytesIO(reference_data))

        # Ensure both files are stereo
        if len(target_audio.shape) == 1:
            target_audio = np.column_stack((target_audio, target_audio))
        if len(reference_audio.shape) == 1:
            reference_audio = np.column_stack((reference_audio, reference_audio))

        # Apply Matchering
        result = mg.process(
            target=target_audio,
            reference=reference_audio,
            target_sr=target_sr,
            reference_sr=reference_sr,
        )

        # Write the mastered audio to an in-memory buffer
        with io.BytesIO() as buf:
            sf.write(buf, result["mastered"], target_sr, format="WAV")
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")

        return encoded
    except Exception as e:
        logger.error(f"Auto mastering failed: {e!s}")
        raise RuntimeError(f"Auto mastering failed: {e!s}")


async def transcribe(file: UploadFile) -> str:
    """Transcribe audio using Whisper"""
    try:
        # Save the uploaded file temporarily
        temp_path = await save_temp_file(file)

        # Transcribe using Whisper
        result = whisper_model.transcribe(temp_path)
        return result["text"]
    except Exception as e:
        raise RuntimeError(f"Transcription failed: {e!s}")


def clone_voice(file: UploadFile):
    # Dummy implementation using Tacotron2 + VITS
    return "Cloned voice result"


def midi_to_audio(file: UploadFile):
    # Dummy implementation using DDSP
    return "Converted MIDI to audio result"


async def generate_music(prompt: str) -> bytes:
    """Generate music from a text prompt (functionality removed: riffusion is no longer maintained)"""
    raise NotImplementedError(
        "Music generation is not available as riffusion is no longer maintained.",
    )


async def search_by_sound(file: UploadFile) -> list:
    """Search for similar sounds"""
    try:
        audio = await file.read()
        embedding = openl3_model(audio)
        distances, indices = index.search(embedding, k=5)
        return indices.tolist()
    except Exception as e:
        raise RuntimeError(f"Audio search failed: {e!s}")


def identify_song(file: UploadFile):
    # Dummy audio fingerprinting implementation
    return "Identified song information"


def detect_genre(file: UploadFile):
    # Dummy genre classification implementation
    return "Detected genre result"


async def apply_effects(file: UploadFile, effects: list) -> bytes:
    """Apply audio effects using TorchAudio"""
    try:
        audio = await file.read()
        waveform, sample_rate = torchaudio.load(audio)
        for effect in effects:
            waveform = torchaudio.functional.apply_effect(waveform, effect)
        return waveform
    except Exception as e:
        raise RuntimeError(f"Audio effects failed: {e!s}")


# Cache for processed chunks
CHUNK_CACHE = {}
CACHE_SIZE_LIMIT = 1000  # Maximum number of chunks to cache


@lru_cache(maxsize=1000)
def process_chunk(chunk_hash: str, model):
    """Process a chunk using the cached result if available."""
    chunk_tensor = CHUNK_CACHE[chunk_hash]["tensor"]
    return model(chunk_tensor)


def get_chunk_hash(chunk: torch.Tensor) -> str:
    """Generate a hash for a chunk of audio."""
    # Convert to numpy and get bytes
    chunk_bytes = chunk.cpu().numpy().tobytes()
    # Generate hash
    return hashlib.md5(chunk_bytes).hexdigest()


def cache_chunk(chunk: torch.Tensor, chunk_hash: str):
    """Cache a chunk with its hash."""
    # Remove oldest item if cache is full
    if len(CHUNK_CACHE) >= CACHE_SIZE_LIMIT:
        oldest_key = next(iter(CHUNK_CACHE))
        del CHUNK_CACHE[oldest_key]

    CHUNK_CACHE[chunk_hash] = {
        "tensor": chunk,
        "timestamp": time.time(),
    }


# Initialize Demucs model at module level
demucs_model = get_model("mdx_extra")  # Use the MDX-Extra music separation model
demucs_model.eval()
if torch.cuda.is_available():
    demucs_model = demucs_model.cuda()


# Create a global thread pool executor
PROCESS_EXECUTOR = ThreadPoolExecutor(max_workers=4)  # Adjust based on CPU cores


async def denoise_music(
    file: UploadFile,
    work_dir: str = None,
    progress_callback: callable = None,
) -> dict:
    """Denoise music using Demucs denoising model with isolated working directory."""
    try:
        logger.info("🎵 Starting music denoising process")
        start_time = time.time()

        # Create work directory if not provided
        if work_dir is None:
            work_dir = tempfile.mkdtemp(prefix="denoise_")

        # Use work_dir for temporary files
        temp_path = os.path.join(work_dir, "input.wav")

        # Save the uploaded file to work directory
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"📁 Saved uploaded file to: {temp_path}")

        if progress_callback:
            await progress_callback(10)
            logger.info("📊 File saved: 10%")

        # Load audio using torchaudio
        waveform, sample_rate = torchaudio.load(temp_path)

        # Ensure stereo
        if waveform.shape[0] == 1:
            waveform = waveform.repeat(2, 1)
        elif waveform.shape[0] > 2:
            waveform = waveform[:2]  # Take first two channels

        # Add batch dimension
        waveform = waveform.unsqueeze(0)

        if torch.cuda.is_available():
            waveform = waveform.cuda()

        # Process in chunks
        chunk_size = 10 * sample_rate  # 10 second chunks
        total_chunks = (waveform.shape[-1] + chunk_size - 1) // chunk_size
        processed_chunks = []

        # Process in chunks using thread pool
        loop = asyncio.get_event_loop()

        for i in range(total_chunks):
            start = i * chunk_size
            end = min(start + chunk_size, waveform.shape[-1])
            chunk = waveform[..., start:end].clone()

            # Offload processing to thread pool
            processed = await loop.run_in_executor(
                PROCESS_EXECUTOR,
                process_chunk_sync,  # Synchronous processing function
                chunk,
                demucs_model,
                i,  # Pass chunk index for logging
            )

            processed_chunks.append(processed.cpu())

            # Update progress
            if progress_callback:
                progress = min(int((i + 1) * 80 / total_chunks) + 10, 90)
                await progress_callback(progress)
                logger.info(f"📊 Processing progress: {progress}%")

        # Combine chunks
        denoised = torch.cat(processed_chunks, dim=-1)
        denoised = denoised.squeeze(0)  # Remove batch dimension

        # Ensure the tensor is 2D (channels x samples)
        if len(denoised.shape) != 2:
            if len(denoised.shape) == 3:
                denoised = denoised.squeeze(0)  # Remove any extra batch dimension
            elif len(denoised.shape) == 1:
                denoised = denoised.unsqueeze(0)  # Add channel dimension

        # Ensure the tensor is on CPU and in the correct format
        denoised = denoised.cpu().float()

        # Log tensor shape for debugging
        logger.debug(f"Final tensor shape before saving: {denoised.shape}")

        # Save result to work directory
        output_path = os.path.join(work_dir, "output.wav")
        torchaudio.save(output_path, denoised, sample_rate)
        logger.info(f"💾 Saved processed file: {output_path}")

        if progress_callback:
            await progress_callback(100)
            logger.info("Final progress: 100%")

        logger.info(f"✅ Processing complete in {time.time() - start_time:.2f}s")
        return {"status": "success", "file_path": output_path}

    except Exception as e:
        logger.error(f"❌ Error during music denoising in {work_dir}: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))


def process_chunk_sync(chunk: torch.Tensor, model, chunk_idx: int):
    """Synchronous chunk processing to run in thread pool"""
    try:
        # Generate hash for chunk
        chunk_hash = get_chunk_hash(chunk)

        # Check cache
        if chunk_hash in CHUNK_CACHE:
            processed = process_chunk(
                chunk_hash,
                lambda x: apply_model(model, x),
            )
            logger.debug(f"✅ Cache hit for chunk {chunk_idx}")
            return processed

        # Process chunk and cache result
        with torch.no_grad():
            processed = apply_model(model, chunk)
        cache_chunk(chunk, chunk_hash)
        logger.debug(f"❌ Cache miss for chunk {chunk_idx}")
        return processed

    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
