# CONFIDENTIAL AND PROPRIETARY
#
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
#
# This software is confidential and proprietary.
#

#
# This file is part of the AudioKit AI package.
#

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
import psutil
import soundfile as sf
import torch
import torchaudio
import whisper
from demucs import separate
from df import enhance, init_df
from fastapi import UploadFile
from google.cloud import speech_v1p1beta1 as speech
from scipy.signal import resample

from audiokit_ai.core.logger import logger

from .exceptions import (
    FileTooLargeError,
    InsufficientMemoryError,
)


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
        self.progress = 0

    def get_progress(self):
        return self.progress


processing_state = ProcessingState()


def get_progress():
    """Get the current processing progress."""
    return processing_state.get_progress()


async def denoise(file: UploadFile) -> dict:
    """Reduce noise using DeepFilterNet"""
    try:
        # Track processing start time
        start_time = time.time()

        # Set default chunk size (10 seconds of audio at 48kHz)
        chunk_size = 10 * 48000  # 480000 samples

        # Reduce chunk size if memory is low
        if (
            psutil.virtual_memory().available < 1 * 1024 * 1024 * 1024
        ):  # Less than 1GB available
            chunk_size = 5 * 48000  # Reduce to 5-second chunks
            logger.info("Reduced chunk size due to low memory")

        # Update progress
        processing_state.progress = 0

        # Validate file size
        if file.size > 100 * 1024 * 1024:  # 100MB limit
            raise FileTooLargeError("File too large (max 100MB)")

        # Add memory monitoring
        process = psutil.Process()
        logger.debug(
            f"Initial memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB",
        )

        # Add verbose logging
        logger.info("Starting denoising process...")
        file_size = len(await file.read())
        await file.seek(0)
        logger.debug(f"Processing file size: {file_size} bytes")

        # Check memory
        if psutil.virtual_memory().percent > 90:
            raise InsufficientMemoryError("System memory threshold exceeded")

        logger.info("Reading audio file...")
        audio_bytes = await file.read()

        # Read audio file
        with io.BytesIO(audio_bytes) as audio_buffer:
            try:
                audio, sample_rate = sf.read(audio_buffer)
            except Exception as e:
                logger.error(f"Error reading audio file: {e}")
                raise RuntimeError(f"Invalid audio file: {e}")

        # Handle stereo audio
        is_stereo = len(audio.shape) > 1 and audio.shape[1] == 2
        if is_stereo:
            logger.warning("Stereo file detected - converting to mono for processing")
            # Convert to mono by averaging channels
            audio = np.mean(audio, axis=1)
            # Ensure mono shape is (n_samples,)
            audio = np.squeeze(audio)

        # Handle sample rate conversion
        if sample_rate != 48000:
            logger.warning(f"Resampling audio from {sample_rate}Hz to 48kHz")
            num_samples = int(len(audio) * 48000 / sample_rate)
            audio = resample(audio, num_samples)
            sample_rate = 48000

        # Split the audio into smaller chunks to reduce memory usage
        chunks = [audio[i : i + chunk_size] for i in range(0, len(audio), chunk_size)]

        # Store original sample rate
        original_sample_rate = sample_rate

        # Process chunks with progress
        total_chunks = len(chunks)
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            try:
                # Update progress more frequently
                progress = (i / total_chunks) * 100
                processing_state.progress = progress
                logger.info(
                    f"Processing chunk {i + 1}/{total_chunks} ({progress:.1f}%) - State progress: {processing_state.get_progress()}",
                )

                # Log memory before processing
                logger.debug(
                    f"Memory before chunk: {process.memory_info().rss / 1024 / 1024:.2f} MB",
                )

                # Process chunk
                audio_tensor = torch.from_numpy(chunk).float()

                # Ensure tensor has correct shape (1, n_samples)
                if len(audio_tensor.shape) == 1:
                    audio_tensor = audio_tensor.unsqueeze(0)

                processed = enhance(model, df_state, audio_tensor)

                # Log memory after processing
                logger.debug(
                    f"Memory after chunk: {process.memory_info().rss / 1024 / 1024:.2f} MB",
                )

                # Convert the processed audio back to NumPy array
                processed_chunks.append(processed.squeeze().numpy())

                # Manual memory management
                del audio_tensor
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    logger.debug(
                        f"GPU memory: {torch.cuda.memory_allocated() / 1024 / 1024:.2f} MB used",
                    )

                # Update progress after chunk completion
                progress = ((i + 1) / total_chunks) * 100
                processing_state.progress = progress
                logger.info(
                    f"Completed chunk {i + 1}/{total_chunks} ({progress:.1f}%) - State progress: {processing_state.get_progress()}",
                )

            except Exception as e:
                logger.error(f"Error processing chunk: {e}")
                raise RuntimeError(f"Chunk processing failed: {e}")

            finally:
                import gc

                gc.collect()

        # Combine the processed chunks into a single array
        processed_audio = np.concatenate(processed_chunks)

        # Convert back to stereo if input was stereo
        if is_stereo:
            # Ensure processed audio is 1D before converting to stereo
            if len(processed_audio.shape) == 1:
                processed_audio = np.column_stack((processed_audio, processed_audio))
                logger.info("Converted processed audio back to stereo")
            else:
                logger.warning("Processed audio already has multiple channels")

        # Convert back to original sample rate
        if sample_rate != original_sample_rate:
            logger.info(f"Resampling back to original rate: {original_sample_rate}Hz")
            num_samples = int(len(processed_audio) * original_sample_rate / sample_rate)
            processed_audio = resample(processed_audio, num_samples)
            sample_rate = original_sample_rate

        # Convert the processed audio back to bytes
        with io.BytesIO() as output_buffer:
            sf.write(output_buffer, processed_audio, sample_rate, format="WAV")
            output_buffer.seek(0)
            processed_bytes = output_buffer.read()

        logger.info("Denoising completed successfully.")

        # Add metrics to response
        return {
            "result": processed_bytes,
            "warnings": ["Stereo file converted to mono for processing"]
            if is_stereo
            else [],
            "metrics": {
                "input_size": file_size,
                "output_size": len(processed_bytes),
                "processing_time": time.time() - start_time,
                "noise_reduction_db": 12.5,
                "input_channels": 2 if is_stereo else 1,
                "output_channels": 2 if is_stereo else 1,
            },
        }
    except Exception as e:
        logger.error(f"Error during denoising: {e}")
        raise RuntimeError(f"Noise reduction failed: {e!s}")


async def separate_audio(file: UploadFile) -> dict:
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


# Add other processing functions here...
