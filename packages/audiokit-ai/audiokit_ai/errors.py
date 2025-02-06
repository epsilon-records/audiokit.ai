"""Error handling for AudioKit AI service."""
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class AudioKitError(HTTPException):
    """Base class for AudioKit errors."""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra = extra or {}

class InvalidAPIKeyError(AudioKitError):
    """Raised when API key is invalid or missing."""
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Invalid or missing API key",
            error_code="INVALID_API_KEY"
        )

class InvalidAudioError(AudioKitError):
    """Raised when audio data is invalid."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=400,
            detail=f"Invalid audio data: {detail}",
            error_code="INVALID_AUDIO"
        )

class ProcessingError(AudioKitError):
    """Raised when audio processing fails."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=500,
            detail=f"Processing failed: {detail}",
            error_code="PROCESSING_ERROR"
        )

class GenerationError(AudioKitError):
    """Raised when audio generation fails."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=500,
            detail=f"Generation failed: {detail}",
            error_code="GENERATION_ERROR"
        )

class RateLimitError(AudioKitError):
    """Raised when rate limit is exceeded."""
    def __init__(self, retry_after: int):
        super().__init__(
            status_code=429,
            detail="Rate limit exceeded",
            error_code="RATE_LIMIT",
            extra={"retry_after": retry_after}
        )

async def error_handler(request: Request, exc: AudioKitError) -> JSONResponse:
    """Global error handler for AudioKit errors."""
    logger.error(
        f"Error handling request: {exc.detail}",
        extra={
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
            **exc.extra
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "details": exc.extra
            }
        }
    ) 