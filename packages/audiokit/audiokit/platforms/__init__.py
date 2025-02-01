"""Platform processors for various music industry services"""

from .base import (
    PlatformProcessor,
    ResponseModel,
    PlatformError,
    AuthError,
    RateLimitError,
    RateLimiter,
)

__all__ = [
    "PlatformProcessor",
    "ResponseModel",
    "PlatformError",
    "AuthError",
    "RateLimitError",
    "RateLimiter",
]
