"""Base classes for platform integrations"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, TypeVar, Generic
import asyncio
import httpx
from pydantic import BaseModel, Field

from ..logger import Logger
from ..models import ArtistData


class RateLimiter:
    """Rate limiter for API requests"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.time_window = 60  # seconds
        self.requests = []

    async def acquire(self):
        """Acquire a rate limit token"""
        now = datetime.now()

        # Remove old requests
        self.requests = [
            ts for ts in self.requests if now - ts < timedelta(seconds=self.time_window)
        ]

        # Check if we're at the limit
        if len(self.requests) >= self.requests_per_minute:
            # Wait until the oldest request expires
            wait_time = (
                self.requests[0] + timedelta(seconds=self.time_window) - now
            ).total_seconds()
            if wait_time > 0:
                Logger.warning(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)

        # Add current request
        self.requests.append(now)


class PlatformError(Exception):
    """Base exception for platform-related errors"""

    pass


class AuthError(PlatformError):
    """Authentication-related errors"""

    pass


class RateLimitError(PlatformError):
    """Rate limit exceeded errors"""

    pass


class ResponseModel(BaseModel):
    """Base model for standardized platform responses"""

    platform: str
    timestamp: datetime = Field(default_factory=datetime.now)
    raw_data: Dict[str, Any]


T = TypeVar("T", bound=ResponseModel)


class PlatformProcessor(Generic[T], ABC):
    """Base class for platform processors"""

    def __init__(self, artist_data: ArtistData):
        self.artist_data = artist_data
        self.rate_limiter = RateLimiter()
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()

    @abstractmethod
    async def authenticate(self) -> None:
        """Authenticate with the platform"""
        pass

    @abstractmethod
    async def fetch_data(self) -> T:
        """Fetch data from the platform"""
        pass

    @abstractmethod
    def transform_response(self, response: Dict[str, Any]) -> T:
        """Transform raw API response into standardized format"""
        pass

    async def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request with rate limiting and error handling"""
        await self.rate_limiter.acquire()

        try:
            response = await self.client.request(
                method=method, url=url, params=params, json=json, headers=headers
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthError("Authentication failed")
            elif e.response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            else:
                Logger.error(f"HTTP error: {str(e)}")
                raise PlatformError(f"HTTP error: {str(e)}")

        except Exception as e:
            Logger.error(f"Unexpected error: {str(e)}")
            raise PlatformError(f"Unexpected error: {str(e)}")

    async def process(self) -> T:
        """Main processing pipeline"""
        try:
            await self.authenticate()
            data = await self.fetch_data()
            return data

        except Exception as e:
            Logger.error(f"Processing failed: {str(e)}")
            raise
