from fastapi import FastAPI
from mcp_sdk import MCPServer
from pydantic import BaseModel


app = FastAPI()
mcp_server = MCPServer(app)


class IngestionRequest(BaseModel):
    audio_path: str | None = None
    text: str | None = None
    file_path: str | None = None


@mcp_server.resource("ingestion")
class IngestionResource:
    @mcp_server.operation("ingest")
    async def ingest(self, request: IngestionRequest):
        """
        Unified ingestion endpoint for audio, text, and file data.
        """
        from pipelines.ingestion_pipeline import run_ingestion_pipeline

        return run_ingestion_pipeline(
            request.audio_path,
            request.text,
            request.file_path,
        )
