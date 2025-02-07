"""FastAPI backend for AudioKit."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from . import processing
from . import auth
from audiokit_core.config import load_config, AudioKitConfig
from audiokit_core.logging import setup_logging
from audiokit_core.routers import health

# Configure logger
logger = logging.getLogger(__name__)

def create_app(config: AudioKitConfig) -> FastAPI:
    """Create FastAPI application with configuration."""
    config = load_config(config.config_path)
    
    # Setup logging first
    setup_logging(config.logging)
    
    app = FastAPI(
        title="AudioKit AI",
        version=config.version,
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )

    # Apply configuration
    app.state.config = config
    
    # Initialize API keys
    auth.init_api_keys(config)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Setup logging
    logger.info(f"Starting server with config: {config.json()}")

    # Register routes
    app.include_router(auth.router)
    app.include_router(processing.router, prefix="/api/v1")
    app.include_router(health.router, prefix="/api/v1")

    return app

class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app, max_upload_size: int):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request, call_next):
        if request.method == "POST":
            content_length = request.headers.get("content-length")
            if content_length:
                content_length = int(content_length)
                if content_length > self.max_upload_size:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": f"File too large. Maximum size is {self.max_upload_size/1024/1024:.1f}MB"
                        }
                    )
        return await call_next(request) 