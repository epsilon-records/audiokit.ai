"""FastAPI backend for AudioKit."""
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from . import processing
from . import auth
from . import monitoring
from .models import AudioAnalysis
from .config import load_config, ServerConfig
from .logging import setup_logging

# Configure logger
logger = logging.getLogger(__name__)

def create_app(config_path: Path = Path("config.yml")) -> FastAPI:
    """Create FastAPI application with configuration."""
    config = load_config(config_path)
    
    app = FastAPI(
        title="AudioKit AI",
        description="Audio analysis API",
        version="0.1.0"
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
    
    # Configure max upload size
    app.add_middleware(
        LimitUploadSize,
        max_upload_size=config.max_file_size
    )
    
    # Setup logging
    setup_logging()
    logger.info(f"Starting server with config: {config.json()}")

    # Register routes
    app.include_router(auth.router)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint.
        
        Returns:
            dict: Health status including version and uptime
        """
        return {
            "status": "healthy",
            "version": app.version,
            "uptime": monitoring.get_uptime(),
            "services": {
                "database": monitoring.check_database_health(),
                "storage": monitoring.check_storage_health()
            }
        }

    @app.post(
        "/analyze",
        response_model=AudioAnalysis,
        tags=["Audio"]
    )
    async def analyze_audio(
        file: UploadFile = File(...),
        token: str = Depends(auth.verify_token)
    ) -> AudioAnalysis:
        """Analyze audio file."""
        try:
            # Log incoming request
            logger.info(f"Analyzing file: {file.filename} ({file.content_type})")
            
            # Add MIME type validation
            allowed_mime_types = ["audio/wav", "audio/mpeg", "audio/ogg", "audio/flac"]
            if file.content_type not in allowed_mime_types:
                logger.warning(f"Unsupported MIME type: {file.content_type}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Allowed types: {', '.join(allowed_mime_types)}"
                )
            
            try:
                contents = await file.read()
                logger.debug(f"Read {len(contents)} bytes from file")
                result = await processing.process_audio(contents)
                return result
            except Exception as e:
                logger.error(f"Processing failed: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=400,
                    detail=f"Audio processing failed: {str(e)}"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Server error: {str(e)}"
            )

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