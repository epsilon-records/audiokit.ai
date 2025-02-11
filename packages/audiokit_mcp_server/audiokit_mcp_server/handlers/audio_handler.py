# handlers/audio_handler.py

import os
from typing import Optional

import weaviate
from fastapi import HTTPException
from pydantic import BaseModel

from audiokit_mcp_server.core.config import settings


# Define request models for ingestion and search
class AudioIngestRequest(BaseModel):
    """Request model for audio ingestion"""

    file_path: str
    metadata: Optional[dict] = None


class AudioSearchRequest(BaseModel):
    """Request model for audio search"""

    query: str
    limit: int = 10


class AudioHandler:
    """Handler for audio ingestion and search using Weaviate"""

    def __init__(self):
        # Initialize Weaviate client with proper constructor arguments
        self.client = weaviate.Client(
            url=settings.WEAVIATE_URL,  # Changed from host to url
            auth_client_secret=weaviate.AuthApiKey(api_key=settings.WEAVIATE_API_KEY),
        )

        # Ensure schema exists
        self._ensure_schema()

    def _ensure_schema(self):
        """Ensure the required Weaviate schema exists"""
        schema = {
            "class": "Audio",
            "properties": [
                {
                    "name": "filePath",
                    "dataType": ["string"],
                },
                {
                    "name": "metadata",
                    "dataType": ["object"],
                },
            ],
        }

        try:
            self.client.schema.create_class(schema)
        except weaviate.exceptions.UnexpectedStatusCodeException:
            # Class might already exist
            pass


# Create singleton instance
audio_handler = AudioHandler()


async def ingest_audio(request: AudioIngestRequest):
    """Ingest audio file metadata into Weaviate"""
    try:
        # Validate file exists
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail="Audio file not found")

        # Create Weaviate object
        audio_handler.client.data_object.create(
            class_name="Audio",
            data_object={
                "filePath": request.file_path,
                "metadata": request.metadata or {},
            },
        )

        return {"status": "success", "message": "Audio ingested successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def search_audio(request: AudioSearchRequest):
    """Search for audio files using vector similarity"""
    try:
        # Perform vector search
        result = (
            audio_handler.client.query.get("Audio", ["filePath", "metadata"])
            .with_near_text({"concepts": [request.query]})
            .with_limit(request.limit)
            .do()
        )

        return result.get("data", {}).get("Get", {}).get("Audio", [])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
