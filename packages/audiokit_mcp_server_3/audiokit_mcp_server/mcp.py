from fastapi import APIRouter, Body
from pydantic import BaseModel
from structlog import get_logger

from .config import Settings
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

    def _setup_routes(self):
        """Setup MCP routes."""
        self.router.post("/process")(self.process)

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
