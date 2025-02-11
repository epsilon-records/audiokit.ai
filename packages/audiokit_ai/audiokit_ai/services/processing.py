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
import io
import json
import os
import tempfile
import time

import faiss
import matchering as mg
import numpy as np
import openl3
import soundfile as sf
import torch
import torchaudio
import whisper
from demucs import separate
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


async def denoise_music(file: UploadFile, progress_callback: callable = None) -> dict:
    """Denoise music using Open-Unmix source separation model for enhanced audio."""
    try:
        logger.info("🎵 Starting music denoising process using Open-Unmix")
        start_time = time.time()

        # Save the uploaded file temporarily
        temp_path = await save_temp_file(file)
        logger.info(f"📁 Saved uploaded file to: {temp_path}")

        if progress_callback:
            await progress_callback(10)
            logger.info("📊 File saved: 10%")

        # Load audio file using TorchAudio
        logger.info(f"🎧 Loading audio file: {file.filename}")
        waveform, sr = torchaudio.load(temp_path)
        logger.info(
            f"📊 Audio specs - Channels: {waveform.shape[0]}, Sample rate: {sr}, Duration: {waveform.shape[1] / sr:.2f}s",
        )

        # Ensure stereo: if mono, replicate channels
        if waveform.shape[0] == 1:
            waveform = waveform.repeat(2, 1)
            logger.info("🔊 Converted mono to stereo")

        if progress_callback:
            await progress_callback(20)
            logger.info("📊 Audio loaded: 20%")

        # Determine device and move waveform to device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        waveform = waveform.to(device)

        # Load Open-Unmix model from torch.hub
        logger.info("🔄 Loading Open-Unmix model (umxl)")
        separator = torch.hub.load("sigsep/open-unmix-pytorch", "umxl", device=device)
        separator.eval()
        logger.info("✅ Open-Unmix model loaded")

        if progress_callback:
            await progress_callback(40)
            logger.info("📊 Model loaded: 40%")

        # Run separation using Open-Unmix
        with torch.no_grad():
            estimates = separator(waveform)

        # Handle output from Open-Unmix: ensure dict format.
        # If a tensor is returned, wrap it in a dict as 'vocals'
        if isinstance(estimates, torch.Tensor):
            estimates = {"vocals": estimates}
            logger.info(
                "ℹ️ Open-Unmix returned tensor output, treating it as 'vocals' stem",
            )
        else:
            logger.info("ℹ️ Open-Unmix returned dictionary of separated sources")

        if progress_callback:
            await progress_callback(60)
            logger.info("📊 Separation complete: 60%")

        # Mix the separated sources to reconstruct a denoised audio.
        # Here we assume that if multiple stems are available (vocals, drums, bass, other)
        # we sum them with a reduced gain for 'other' to help reduce noise.
        if "vocals" in estimates and len(estimates) > 1:
            vocals = estimates.get("vocals", 0)
            drums = estimates.get("drums", 0)
            bass = estimates.get("bass", 0)
            other = estimates.get("other", 0)
            denoised = vocals + drums + bass + 0.5 * other
            logger.info("✅ Mixed multiple stems for denoised output")
        else:
            # If only a single stem is returned, use it directly.
            denoised = list(estimates.values())[0]
            logger.info("✅ Single stem available, using it for denoised output")

        # Ensure the denoised audio is on CPU
        denoised = denoised.cpu()

        if progress_callback:
            await progress_callback(80)
            logger.info("📊 Mixing complete: 80%")

        # Save the processed file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            torchaudio.save(temp_file.name, denoised, sr)
            output_path = temp_file.name
            logger.info(f"💾 Saved denoised file: {output_path}")

        if progress_callback:
            await progress_callback(100)
            logger.info("Final progress: 100%")

        logger.info(f"✅ Processing complete in {time.time() - start_time:.2f}s")
        return {"status": "success", "file_path": output_path}

    except Exception as e:
        logger.error(f"❌ Error during music denoising with Open-Unmix: {e}")
        raise HTTPException(status_code=500, detail=str(e))
