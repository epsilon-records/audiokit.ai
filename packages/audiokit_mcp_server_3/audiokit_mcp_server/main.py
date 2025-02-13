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
        await cache.ping()
        return {"status": "ok"}
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        raise HTTPException(status_code=500, detail="Redis connection failed")


def setup_cache():
    try:
        caches.set_config(
            {
                "default": {
                    "cache": "aiocache.RedisCache",
                    "endpoint": settings.redis_url.split("://")[1].split(":")[0],
                    "port": int(settings.redis_url.split(":")[-1].split("/")[0]),
                    "db": int(settings.redis_url.split("/")[-1]),
                    "timeout": 5,
                    "serializer": {
                        "class": "aiocache.serializers.JsonSerializer",
                    },
                },
            },
        )
        logger.info(
            "✅ Redis cache configured",
            url=settings.redis_url,
            timeout=5,
        )
    except Exception as e:
        logger.error(
            "❌ Failed to configure Redis cache",
            error=str(e),
        )
        raise


# Call this during app initialization
setup_cache()
