"""FastAPI backend for AudioKit."""
from typing import Dict, Optional
from fastapi import FastAPI, File, UploadFile, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from . import processing
from . import generation
from . import models
from . import errors
from . import auth

app = FastAPI(title="AudioKit AI")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handlers
app.add_exception_handler(errors.AudioKitError, errors.error_handler)

@app.post("/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    token: auth.TokenData = Depends(auth.verify_permission("analyze"))
):
    """Analyze audio file and return properties."""
    try:
        contents = await file.read()
        return await processing.analyze_audio(contents)
    except ValueError as e:
        raise errors.InvalidAudioError(str(e))
    except Exception as e:
        raise errors.ProcessingError(str(e))

@app.post("/generate")
async def generate_audio(
    params: generation.GenerationParameters,
    token: auth.TokenData = Depends(auth.verify_permission("generate"))
):
    """Generate audio using AI models."""
    try:
        audio_array, sr = await generation.generate_audio(params)
        return {
            "audio": audio_array.tolist(),
            "sample_rate": sr,
            "duration": len(audio_array) / sr
        }
    except Exception as e:
        raise errors.GenerationError(str(e))

@app.post("/generate/with-style")
async def generate_with_style(
    params: generation.GenerationParameters,
    reference: Optional[UploadFile] = File(None),
    token: auth.TokenData = Depends(auth.verify_permission("generate"))
):
    """Generate audio matching the style of reference audio."""
    try:
        reference_data = await reference.read() if reference else None
        audio_array, sr = await generation.generate_with_style(params, reference_data)
        return {
            "audio": audio_array.tolist(),
            "sample_rate": sr,
            "duration": len(audio_array) / sr
        }
    except ValueError as e:
        raise errors.InvalidAudioError(str(e))
    except Exception as e:
        raise errors.GenerationError(str(e)) 