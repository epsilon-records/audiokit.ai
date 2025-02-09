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

import faiss
import matchering as mg
import numpy as np
import openl3
import soundfile as sf
import torchaudio
import whisper
from demucs import separate
from df import enhance, init_df
from fastapi import UploadFile
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


async def denoise(file: UploadFile) -> bytes:
    """Reduce noise using DeepFilterNet"""
    try:
        # Load audio
        audio = await file.read()

        # Process with DeepFilterNet
        processed = enhance(model, df_state, audio)

        return processed
    except Exception as e:
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
