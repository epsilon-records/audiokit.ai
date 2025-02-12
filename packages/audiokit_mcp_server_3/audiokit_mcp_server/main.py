from fastapi import FastAPI
from structlog import get_logger

from .config import Settings
from .mcp import MCPRouter


logger = get_logger()

app = FastAPI(
    title="AudioKit MCP Server",
    description="AudioKit Model Context Protocol Server Implementation",
    version="3.0.0",
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting AudioKit MCP Server")
    settings = Settings()
    mcp_router = MCPRouter()
    app.include_router(mcp_router.router, prefix="/mcp", tags=["mcp"])
