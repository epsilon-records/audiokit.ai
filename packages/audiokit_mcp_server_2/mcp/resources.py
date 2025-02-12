from typing import Optional

from mcp_sdk import MCPResource
from pydantic import BaseModel


class IngestionRequest(BaseModel):
    audio_path: Optional[str] = None
    text: Optional[str] = None
    file_path: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class ProcessingRequest(BaseModel):
    file_path: str


@mcp_server.resource("audiokit")
class AudioKitResource(MCPResource):
    """AudioKit MCP Resource for audio processing and knowledge operations"""

    @mcp_server.operation("ingest")
    async def ingest(self, request: IngestionRequest):
        """Ingest audio, text, or file data into the knowledge base"""
        from ..pipelines.ingestion_pipeline import run_ingestion_pipeline

        return run_ingestion_pipeline(
            request.audio_path,
            request.text,
            request.file_path,
        )

    @mcp_server.operation("query")
    async def query(self, request: QueryRequest):
        """Query the knowledge base"""
        from ..pipelines.query_pipeline import run_query_pipeline

        return run_query_pipeline(request.query)

    @mcp_server.operation("process")
    async def process(self, request: ProcessingRequest):
        """Process audio files"""
        from ..pipelines.processing_pipeline import run_processing_pipeline

        return run_processing_pipeline(request.file_path)
