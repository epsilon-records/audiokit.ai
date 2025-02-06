"""FastAPI backend for AudioKit."""
from typing import Dict, Optional
from fastapi import FastAPI, File, UploadFile, Header, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import io

from . import processing
from . import generation
from . import models
from . import errors
from . import auth
from .cache import Cache, CacheConfig

app = FastAPI(
    title="AudioKit AI",
    description="Audio processing and analysis API",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handlers
app.add_exception_handler(errors.AudioKitError, errors.error_handler)

# Initialize cache
cache_config = CacheConfig()
cache = Cache(cache_config)

@app.post(
    "/analyze",
    response_model=models.AudioAnalysis,
    tags=["Audio Analysis"]
)
@cached(ttl=3600, tags=["analysis"])  # Cache analysis results for 1 hour
async def analyze_audio(
    file: UploadFile = File(...),
    sample_rate: Optional[int] = None,
    token: auth.TokenData = Depends(auth.verify_permission("analyze"))
) -> models.AudioAnalysis:
    """Analyze audio file and extract features.
    
    Args:
        file: Audio file to analyze
        sample_rate: Optional target sample rate
        token: API token with permissions
        
    Returns:
        Audio analysis results
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        contents = await file.read()
        return await processing.analyze_audio(
            contents,
            filename=file.filename,
            sample_rate=sample_rate
        )
    except errors.ProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

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

@app.post(
    "/process",
    tags=["Audio Processing"]
)
async def process_audio(
    file: UploadFile = File(...),
    params: models.ProcessingParameters,
    token: auth.TokenData = Depends(auth.verify_permission("process"))
) -> StreamingResponse:
    """Process audio file with effects.
    
    Args:
        file: Audio file to process
        params: Processing parameters
        token: API token with permissions
        
    Returns:
        Processed audio file
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        contents = await file.read()
        audio_array, sample_rate = await processing.process_audio(contents, params)
        
        # Convert to WAV bytes
        output = io.BytesIO()
        processing.save_audio(audio_array, sample_rate, output)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'attachment; filename="processed_{file.filename}"'
            }
        )
    except errors.ProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Admin endpoints for API key management
@app.post(
    "/admin/keys",
    response_model=auth.APIKey,
    tags=["Admin"]
)
async def create_key(
    name: str,
    permissions: Optional[list[str]] = None,
    token: auth.TokenData = Depends(auth.verify_permission("admin"))
) -> auth.APIKey:
    """Create new API key.
    
    Args:
        name: Key name/description
        permissions: Optional permission list
        token: Admin API token
        
    Returns:
        Created API key
    """
    return auth.create_api_key(name, permissions)

# Health check endpoint
@app.get("/health")
async def health_check() -> dict:
    """Check API health."""
    return {"status": "healthy"} 