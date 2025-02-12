from contextlib import asynccontextmanager

from fastapi import FastAPI
from structlog import get_logger

from .config import Settings
from .mcp import MCPRouter


logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting AudioKit MCP Server")
        settings = Settings()
        redacted_settings = settings.dict()
        if "pinecone_api_key" in redacted_settings:
            redacted_settings["pinecone_api_key"] = (
                f"******{redacted_settings['pinecone_api_key'][-4:]}"
            )
        if "openrouter_api_key" in redacted_settings:
            redacted_settings["openrouter_api_key"] = (
                f"******{redacted_settings['openrouter_api_key'][-4:]}"
            )
        logger.info("Loaded settings", settings=redacted_settings)
        yield
        logger.info("Shutting down AudioKit MCP Server")
    except Exception as e:
        logger.critical("Startup failed", error=str(e))
        raise


app = FastAPI(
    title="AudioKit MCP Server",
    description="AudioKit Model Context Protocol Server Implementation",
    version="3.0.0",
    lifespan=lifespan,
)

# Mount MCP router at prefix /mcp
mcp_router = MCPRouter()
app.include_router(mcp_router.router, prefix="/mcp", tags=["mcp"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
