import logging
from contextlib import asynccontextmanager

from aiocache import caches
from fastapi import FastAPI, HTTPException
from structlog import configure, get_logger
from structlog.processors import JSONRenderer, TimeStamper
from structlog.stdlib import add_log_level, filter_by_level

from ..config import settings
from .config import Settings
from .mcp import MCPRouter
from .utils.redis import setup_redis_cache


def setup_logging(log_level: str = "INFO"):
    """Configure structlog with the specified log level."""
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
    )

    configure(
        processors=[
            filter_by_level,
            add_log_level,
            TimeStamper(fmt="iso"),
            JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=logging.LoggerFactory(),
        wrapper_class=logging.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logger = get_logger()
    logger.info("Logging configured", level=log_level)
    return logger


logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Initialize logging
        setup_logging(settings.log_level)

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

        # Initialize cache
        setup_redis_cache(settings)

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


@app.get("/cache/health")
async def cache_health_check():
    try:
        cache = caches.get("default")
        logger.debug("🏥 Performing Redis health check")
        await cache.ping()
        logger.debug("✅ Redis health check successful")
        return {"status": "ok"}
    except Exception as e:
        logger.error("❌ Redis health check failed", error=str(e))
        raise HTTPException(status_code=500, detail="Redis connection failed")


@app.get("/cache/test")
async def cache_test():
    cache = caches.get("default")
    await cache.set("test_key", "test_value", ttl=60)
    value = await cache.get("test_key")
    return {"status": "success", "value": value}
