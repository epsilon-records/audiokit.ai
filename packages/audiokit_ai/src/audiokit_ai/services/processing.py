from fastapi import UploadFile
import torchaudio
from df import enhance, init_df
from demucs import separate
import whisper
import faiss
import openl3
from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account
import tempfile
import os
from audiokit_ai.core.logger import logger

# Initialize DeepFilterNet using the recommended API
model, df_state, _ = init_df()
whisper_model = whisper.load_model("base")

# Initialize FAISS index and OpenL3 model
index = faiss.IndexFlatL2(512)
openl3_model = openl3.models.load_audio_embedding_model(
    input_repr="mel256",  # Mel-spectrogram with 256 bins
    content_type="music",  # Use "music" for music-related tasks
    embedding_size=512  # Size of the embedding vector
)

# Initialize the SpeechClient
try:
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        credentials = service_account.Credentials.from_service_account_file(
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        )
        client = speech.SpeechClient(credentials=credentials)
    else:
        client = speech.SpeechClient()  # Fallback to ADC
except Exception as e:
    raise RuntimeError(f"Failed to initialize SpeechClient: {str(e)}")

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
        logger.error(f"Failed to save temporary file: {str(e)}")
        raise RuntimeError(f"Failed to save temporary file: {str(e)}")

async def denoise(file: UploadFile) -> bytes:
    """Reduce noise using DeepFilterNet"""
    try:
        # Load audio
        audio = await file.read()
        
        # Process with DeepFilterNet
        processed = enhance(model, df_state, audio)
        
        return processed
    except Exception as e:
        raise RuntimeError(f"Noise reduction failed: {str(e)}")

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
        raise RuntimeError(f"Audio separation failed: {str(e)}")

async def auto_master(file: UploadFile):
    # Dummy implementation using DSPNet + U-Net mastering
    return "Auto mastered audio result"

async def transcribe(file: UploadFile) -> str:
    """Transcribe audio using Whisper"""
    try:
        # Save the uploaded file temporarily
        temp_path = await save_temp_file(file)
        
        # Transcribe using Whisper
        result = whisper_model.transcribe(temp_path)
        return result["text"]
    except Exception as e:
        raise RuntimeError(f"Transcription failed: {str(e)}")

def clone_voice(file: UploadFile):
    # Dummy implementation using Tacotron2 + VITS
    return "Cloned voice result"

def midi_to_audio(file: UploadFile):
    # Dummy implementation using DDSP
    return "Converted MIDI to audio result"

async def generate_music(prompt: str) -> bytes:
    """Generate music from a text prompt (functionality removed: riffusion is no longer maintained)"""
    raise NotImplementedError("Music generation is not available as riffusion is no longer maintained.")

async def search_by_sound(file: UploadFile) -> list:
    """Search for similar sounds"""
    try:
        audio = await file.read()
        embedding = openl3_model(audio)
        distances, indices = index.search(embedding, k=5)
        return indices.tolist()
    except Exception as e:
        raise RuntimeError(f"Audio search failed: {str(e)}")

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
        raise RuntimeError(f"Audio effects failed: {str(e)}")

# Add other processing functions here... 