from fastapi import Request
from .config import AudioKitConfig

class LoggingMiddleware:
    def __init__(self, app, config: AudioKitConfig):
        self.app = app
        self.log_level = config.log_level

    async def __call__(self, request: Request, call_next):
        # Add request logging here
        response = await call_next(request)
        # Add response logging here
        return response 