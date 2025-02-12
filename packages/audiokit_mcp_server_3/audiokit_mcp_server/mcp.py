from typing import Any, Dict

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

    async def process(self, request: QueryRequest = Body(...)) -> Dict[str, Any]:
        """Process an MCP request."""
        try:
            # Process the request using llama_index_service
            query_response = await self.llama_index_service.query(request.query)
            return {
                "status": "success",
                "response": {
                    "answer": query_response["answer"],
                    "sources": query_response["sources"],
                },
            }
        except Exception as e:
            logger.error("Failed to process MCP request", error=str(e))
            return {"status": "error", "message": str(e)}
