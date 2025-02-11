# main.py

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP

from audiokit_mcp_server.core.logger import logger
from audiokit_mcp_server.handlers.analytics_rag import analyze_spotify_uri
from audiokit_mcp_server.handlers.audio_converter import (
    convert_audio,
)
from audiokit_mcp_server.handlers.audio_handler import ingest_audio, search_audio


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
        "weaviate-client",
        "ffmpeg-python",
    ],
)


# Register endpoints as MCP tools
@mcp_server.tool()
async def ingest_audio_tool(request: dict) -> dict:
    """Ingest audio file metadata into Weaviate"""
    return await ingest_audio(request)


@mcp_server.tool()
async def search_audio_tool(request: dict) -> dict:
    """Search for audio files using vector similarity"""
    return await search_audio(request)


@mcp_server.tool()
async def convert_audio_tool(request: dict) -> dict:
    """Convert audio file to different format"""
    return await convert_audio(request)


@mcp_server.tool()
async def analyze_spotify_tool(request: dict) -> dict:
    """Analyze Spotify artist data"""
    return await analyze_spotify_uri(request)


@mcp_server.tool()
async def test_soundcharts_rag(request: dict) -> dict:
    """Test the Soundcharts RAG system with a sample query"""
    try:
        # Test with Drake's Spotify URI
        test_request = {
            "spotify_uri": "spotify:artist:3TVXtAsR1Inumwj472S9r4",
            "query": "What are Drake's top performing songs and their trends over the last year?",
        }
        return await analyze_spotify_uri(test_request)
    except Exception as e:
        logger.error(f"Soundcharts RAG test failed: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))


# Mount FastAPI app
mcp_server.mount_to_fastapi(app)


# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error: {exc.detail}")
    return {"error": exc.detail, "status_code": exc.status_code}


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc!s}")
    return {"error": "Internal server error", "status_code": 500}


if __name__ == "__main__":
    # Run the server using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
