# handlers/audio_handler.py

import os
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from pinecone import Pinecone
from pydantic import BaseModel

from audiokit_mcp_server.core.config import settings
from audiokit_mcp_server.core.embeddings import get_embedding


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
    """Handler for audio ingestion and search using Pinecone"""

    def __init__(self):
        # Initialize Pinecone with new API
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)

        # Use existing audiokit-brain index
        self.index = self.pc.Index("audiokit-brain")

    async def ingest_audio(self, request: AudioIngestRequest):
        """Ingest audio file metadata into Pinecone"""
        try:
            # Validate file exists
            if not os.path.exists(request.file_path):
                raise HTTPException(status_code=404, detail="Audio file not found")

            # Generate embedding from file path or metadata
            vector = await self.get_embedding(request.file_path)

            # Create metadata
            metadata = {
                "file_path": request.file_path,
                **(request.metadata or {}),
            }

            # Generate vector ID
            vector_id = f"audio_{datetime.utcnow().timestamp()}"

            # Upsert to Pinecone
            self.index.upsert([(vector_id, vector, metadata)])

            return {"status": "success", "message": "Audio ingested successfully"}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def search_audio(self, request: AudioSearchRequest):
        """Search for audio files using vector similarity"""
        try:
            # Convert query to vector
            query_vector = await self.get_embedding(request.query)

            # Search Pinecone
            results = self.index.query(
                vector=query_vector,
                top_k=request.limit,
                include_metadata=True,
            )

            return [
                {
                    "file_path": match.metadata["file_path"],
                    "metadata": {
                        k: v for k, v in match.metadata.items() if k != "file_path"
                    },
                }
                for match in results.matches
            ]

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector using OpenAI"""
        return await get_embedding(text)


# Create singleton instance
audio_handler = AudioHandler()

# At the bottom of the file, after creating the singleton instance
# Add these module-level functions that use the singleton


async def ingest_audio(request: dict):
    """Module-level function to ingest audio"""
    return await audio_handler.ingest_audio(AudioIngestRequest(**request))


async def search_audio(request: dict):
    """Module-level function to search audio"""
    return await audio_handler.search_audio(AudioSearchRequest(**request))
