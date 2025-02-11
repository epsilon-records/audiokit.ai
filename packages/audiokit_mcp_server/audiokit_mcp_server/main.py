# main.py

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
from mcp.server.fastmcp import FastMCP

from audiokit_mcp_server.core.config import settings
from audiokit_mcp_server.core.logger import logger
from audiokit_mcp_server.handlers.analytics_rag import analyze_spotify_uri
from audiokit_mcp_server.handlers.audio_converter import (
    convert_audio,
)
from audiokit_mcp_server.handlers.audio_handler import ingest_audio, search_audio
from audiokit_mcp_server.models.spotify_analytics_request import SpotifyAnalyticsRequest


# Create FastAPI application
app = FastAPI(
    title="Audiokit MCP Server",
    description="Music analytics and audio processing server",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP server
mcp_server = FastMCP(
    "AudioKit MCP",
    dependencies=[
        "pandas",
        "numpy",
        "scipy",
        "pinecone-client",
        "ffmpeg-python",
    ],
)

# Create API router
router = APIRouter(prefix="/api/v1")


# Register endpoints
@router.post("/ingest")
async def ingest_audio_endpoint(request: dict):
    """Ingest audio file metadata into vector store"""
    return await ingest_audio(request)


@router.post("/search")
async def search_audio_endpoint(request: dict):
    """Search for audio files using vector similarity"""
    return await search_audio(request)


@router.post("/convert")
async def convert_audio_endpoint(request: dict):
    """Convert audio file to different format"""
    return await convert_audio(request)


@router.post("/analyze/spotify")
async def analyze_spotify_endpoint(request: SpotifyAnalyticsRequest):
    """Analyze Spotify artist data"""
    return await analyze_spotify_uri(request)


@router.post("/test/soundcharts")
async def test_soundcharts_endpoint():
    """Test the Soundcharts RAG system with a sample query"""
    try:
        # Test with Drake's Spotify URI
        test_request = SpotifyAnalyticsRequest(
            spotify_uri="spotify:artist:3TVXtAsR1Inumwj472S9r4",
            query="What are Drake's top performing songs and their trends over the last year?",
        )
        return await analyze_spotify_uri(test_request)
    except Exception as e:
        logger.error(f"Soundcharts RAG test failed: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",  # TODO: Get from package version
        "environment": settings.ENV,
    }


# Include router in app
app.include_router(router)


# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc!s}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500},
    )


# Add after FastAPI initialization
app.mount("/artists", StaticFiles(directory="static/artists"), name="artists")


if __name__ == "__main__":
    # Run the server using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
