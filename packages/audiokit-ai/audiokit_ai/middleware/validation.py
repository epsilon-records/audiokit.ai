"""Request validation and security middleware."""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable, Optional
from datetime import datetime
from audiokit_core.models.schemas import APIErrorResponse
from ..auth import AuthHandler
import logging
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class RequestValidator:
    def __init__(self, auth_handler: AuthHandler):
        self.auth = auth_handler
        self.max_body_size = 100 * 1024 * 1024  # 100MB
        self.request: Optional[Request] = None
        
    async def __call__(self, request: Request, call_next: Callable) -> JSONResponse:
        """Main middleware handler"""
        self.request = request
        try:
            # Phase 1: Pre-Validation
            await self._validate_headers(request)
            await self._validate_client_version(request)
            
            # Phase 2: Body Validation
            if request.method in ["POST", "PUT", "PATCH"]:
                await self._validate_body(request)
            
            # Phase 3: Security Headers
            response = await call_next(request)
            self._add_security_headers(response)
            
            return response
            
        except HTTPException as e:
            return self._error_response(e.status_code, e.detail)
        except ValidationError as _:
            logger.error("Validation failed")
            return self._error_response(500, "Internal server error")

    async def _validate_headers(self, request: Request):
        """Validate required headers"""
        if not request.headers.get("Content-Type", "").startswith("application/"):
            raise HTTPException(415, "Unsupported media type")
            
        if int(request.headers.get("Content-Length", 0)) > self.max_body_size:
            raise HTTPException(413, "Payload too large")

    async def _validate_client_version(self, request: Request):
        """Validate client version compatibility"""
        await self.auth.validate_client_version(request)

    async def _validate_body(self, request: Request):
        """Validate request body structure"""
        body = await request.json()
        if not isinstance(body, dict):
            raise HTTPException(400, "Invalid request format")
            
        if "audio_data" in body and len(body["audio_data"]) > self.max_body_size:
            raise HTTPException(413, "Audio payload exceeds size limit")

    def _add_security_headers(self, response: JSONResponse):
        """Add comprehensive security headers to all responses"""
        security_headers = {
            "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "accelerometer=(), camera=(), geolocation=(), microphone=()",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
            "Cache-Control": "no-store, max-age=0"
        }
        
        # Add security headers without overriding existing ones
        for header, value in security_headers.items():
            if header not in response.headers:
                response.headers[header] = value

    def _error_response(self, status_code: int, detail: str) -> JSONResponse:
        """Standard error response format"""
        error = APIErrorResponse(
            timestamp=datetime.utcnow(),
            status=status_code,
            error=detail,
            path=self._get_request_path(self.request),
        )
        return JSONResponse(
            content=error.dict(),
            status_code=status_code,
            headers={"Content-Type": "application/problem+json"}
        )

    def _get_request_path(self, request: Request) -> str:
        """Extract request path from request object"""
        return request.url.path 