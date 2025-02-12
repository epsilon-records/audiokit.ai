import base64

from fastapi import APIRouter, Body, File, UploadFile
from pydantic import BaseModel
from structlog import get_logger

from .config import Settings
from .services.audio_service import AudioService
from .services.llama_index_service import LlamaIndexService


logger = get_logger()


class QueryRequest(BaseModel):
    """Query request model."""

    query: str


class MCPRouter:
    """MCP Router for handling MCP requests."""

    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        self.settings = Settings()
        self.llama_index_service = LlamaIndexService(self.settings)
        self.audio_service = AudioService(self.settings)

    def _setup_routes(self):
        """Setup MCP routes."""
        self.router.post("/process")(self.process)
        self.router.post("/ingest")(self.ingest)
        self.router.post("/ingest/audio")(self.ingest_audio)

    async def process(self, query: str = Body(...)) -> dict:
        """Process an MCP request."""
        try:
            # Retrieve the answer and sources from the query
            result = await self.llama_index_service.query(query)

            # Write back the LLM output to the vector store so that future queries can improve.
            # Note: writeback_llm_output is a synchronous function; if needed, you can wrap it in
            # an executor to avoid blocking.
            self.llama_index_service.writeback_llm_output(query, result["answer"])

            return {"status": "success", "response": result}
        except Exception as e:
            logger.error("Failed to process MCP request", error=str(e))
            return {"status": "error", "message": str(e)}

    async def ingest(
        self,
        document: str = Body(...),
        metadata: dict = Body(None),
    ) -> dict:
        """Ingest a document into the vector store."""
        try:
            result = self.llama_index_service.ingest_document(document, metadata)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error("Document ingestion failed", error=str(e))
            return {"status": "error", "message": str(e)}

    async def ingest_audio(self, file: UploadFile = File(...)) -> dict:
        """
        Ingest an audio file, generate fingerprint, and store in vector database.
        """
        try:
            # Read audio file
            audio_data = await file.read()

            # Process audio and generate fingerprint
            fingerprint, metadata = await self.audio_service.process_audio(
                audio_data,
                file.filename,
            )

            # Ensure metadata is JSON-serializable
            serializable_metadata = {
                "type": "audio",
                "fingerprint": base64.b64encode(fingerprint).decode("utf-8"),
                "duration": metadata["duration"],
                "sample_rate": metadata["sample_rate"],
                "channels": metadata["channels"],
                "frame_count": metadata["frame_count"],
                "original_filename": metadata["original_filename"],
                "acoustid_results": metadata["acoustid_results"],
            }
            logger.debug("AcoustID results", results=metadata["acoustid_results"])
            logger.debug("Serializable metadata", metadata=serializable_metadata)

            # Create document text from metadata
            document = f"""
            Audio File: {file.filename}
            Duration: {metadata["duration"]}
            Fingerprint: {fingerprint}
            Sample Rate: {metadata["sample_rate"]}
            Channels: {metadata["channels"]}
            """

            # Ingest document with audio metadata
            result = self.llama_index_service.ingest_document(
                document=document,
                metadata=serializable_metadata,
            )
            logger.debug("Document ingestion result", result=result)

            return {
                "status": "success",
                "result": result,
                "fingerprint": fingerprint,
                "metadata": serializable_metadata,
            }

        except Exception as e:
            logger.error("Audio ingestion failed", error=str(e))
            return {"status": "error", "message": str(e)}
