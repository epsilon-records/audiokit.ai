"""FastAPI backend for AudioKit."""
from typing import Dict
from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from . import processing
from . import models

app = FastAPI(title="AudioKit AI")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    x_api_key: str = Header(...)
):
    """Analyze audio file and return properties."""
    # Validate API key here
    
    contents = await file.read()
    return await processing.analyze_audio(contents)

@app.post("/process")
async def process_audio(
    file: UploadFile = File(...),
    x_api_key: str = Header(...)
):
    """Process audio file with AI models."""
    # Validate API key here
    
    contents = await file.read()
    return await processing.process_audio(contents)

@app.post("/generate")
async def generate_content(
    params: Dict,
    x_api_key: str = Header(...)
):
    """Generate audio content from parameters."""
    # Validate API key here
    
    return await processing.generate_content(params)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 