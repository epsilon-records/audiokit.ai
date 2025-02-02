"""Base classes for platform integrations"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, TypeVar, Generic, Callable, TypeAlias
import asyncio
import json
import hashlib
import random
import httpx
from pydantic import BaseModel, Field
import redis.asyncio as redis
from functools import wraps

from ..logger import Logger
from ..models import ArtistData
from config import cfg

# Type alias for async callable
AsyncCallable: TypeAlias = Callable[..., Any]


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


class TokenExpiredError(AuthError):
    """Token expired error"""

    pass


class RefreshTokenError(AuthError):
    """Token refresh error"""

    pass


class CacheConfig(BaseModel):
    """Cache configuration"""

    enabled: bool = True
    ttl: int = 3600  # 1 hour default
    prefix: str = "platform"
    namespace: Optional[str] = None
    invalidation_patterns: list[str] = Field(default_factory=list)


class ResponseModel(BaseModel):
    """Base model for standardized platform responses"""

    platform: str
    timestamp: datetime = Field(default_factory=datetime.now)
    raw_data: Dict[str, Any]
    cache_info: Optional[Dict[str, Any]] = None


class AuthState(BaseModel):
    """Platform authentication state"""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    scopes: list[str] = Field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        """Check if access token is expired"""
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at

    def get_auth_header(self) -> Dict[str, str]:
        """Get authorization header"""
        return {"Authorization": f"{self.token_type} {self.access_token}"}


T = TypeVar("T", bound=ResponseModel)


class RetryConfig(BaseModel):
    """Configuration for retry mechanism"""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 10.0
    retryable_exceptions: tuple = (
        httpx.HTTPError,
        redis.RedisError,
        asyncio.TimeoutError,
        ConnectionError,
        RateLimitError,
    )
    retry_on_status_codes: set[int] = {408, 429, 500, 502, 503, 504}


class PlatformProcessor(Generic[T], ABC):
    """Base class for platform processors"""

    def __init__(self, artist_data: ArtistData):
        self.artist_data = artist_data
        self.rate_limiter = RateLimiter()
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_state: Optional[AuthState] = None
        self.redis = redis.from_url(cfg.redis.url)
        self.cache_config = CacheConfig(
            namespace=f"{self.__class__.__name__.lower()}:{self.artist_data.id}"
        )
        self.retry_config = RetryConfig()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()
        await self.redis.close()

    def _get_cache_key(
        self, method: str, url: str, params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate cache key from request parameters"""
        cache_data = {
            "method": method,
            "url": url,
            "params": params or {},
            "namespace": self.cache_config.namespace,
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        key_hash = hashlib.sha256(cache_str.encode()).hexdigest()
        return f"{self.cache_config.prefix}:{key_hash}"

    async def _get_cached_response(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        try:
            if not self.cache_config.enabled:
                return None

            cached = await self.redis.get(key)
            if cached:
                Logger.info(f"Cache hit for {key}")
                return json.loads(cached)
            return None
        except Exception as e:
            Logger.warning(f"Failed to get cached response: {str(e)}")
            return None

    async def _cache_response(
        self, key: str, response: Dict[str, Any], ttl: Optional[int] = None
    ) -> None:
        """Cache response"""
        try:
            if not self.cache_config.enabled:
                return

            await self.redis.setex(
                key, ttl or self.cache_config.ttl, json.dumps(response)
            )
            Logger.info(f"Cached response for {key}")
        except Exception as e:
            Logger.warning(f"Failed to cache response: {str(e)}")

    async def _invalidate_cache_patterns(self) -> None:
        """Invalidate cache based on patterns"""
        try:
            if not self.cache_config.enabled:
                return

            for pattern in self.cache_config.invalidation_patterns:
                pattern_key = f"{self.cache_config.prefix}:{pattern}"
                keys = await self.redis.keys(pattern_key)
                if keys:
                    await self.redis.delete(*keys)
                    Logger.info(
                        f"Invalidated {len(keys)} cache entries for pattern {pattern}"
                    )
        except Exception as e:
            Logger.warning(f"Failed to invalidate cache: {str(e)}")

    @abstractmethod
    async def _get_auth_credentials(self) -> Dict[str, Any]:
        """Get platform-specific authentication credentials"""
        pass

    @abstractmethod
    async def _refresh_auth_token(self) -> AuthState:
        """Refresh authentication token"""
        pass

    async def _get_cached_auth(self) -> Optional[AuthState]:
        """Get cached authentication state"""
        try:
            key = f"auth:{self.artist_data.id}:{self.__class__.__name__}"
            cached = await self.redis.get(key)
            if cached:
                return AuthState.model_validate_json(cached)
            return None
        except Exception as e:
            Logger.warning(f"Failed to get cached auth: {str(e)}")
            return None

    async def _cache_auth(self, auth: AuthState, ttl: Optional[int] = None):
        """Cache authentication state"""
        try:
            key = f"auth:{self.artist_data.id}:{self.__class__.__name__}"
            await self.redis.setex(
                key,
                ttl or 3600,  # Default 1 hour TTL
                auth.model_dump_json(),
            )
        except Exception as e:
            Logger.warning(f"Failed to cache auth: {str(e)}")

    async def authenticate(self) -> None:
        """Authenticate with the platform"""
        try:
            # Check cache first
            self.auth_state = await self._get_cached_auth()

            if not self.auth_state or self.auth_state.is_expired:
                # Get fresh credentials if no cache or expired
                credentials = await self._get_auth_credentials()

                # Make auth request
                response = await self._make_request(
                    "POST", f"{self.base_url}/oauth/token", json=credentials
                )

                # Parse response into AuthState
                self.auth_state = AuthState(
                    access_token=response["access_token"],
                    refresh_token=response.get("refresh_token"),
                    token_type=response.get("token_type", "Bearer"),
                    expires_at=datetime.now()
                    + timedelta(seconds=response.get("expires_in", 3600)),
                    scopes=response.get("scope", "").split()
                    if response.get("scope")
                    else [],
                )

                # Cache the auth state
                await self._cache_auth(
                    self.auth_state,
                    int((self.auth_state.expires_at - datetime.now()).total_seconds())
                    if self.auth_state.expires_at
                    else None,
                )

            Logger.info(f"Authenticated with {self.__class__.__name__}")

        except Exception as e:
            Logger.error(f"Authentication failed: {str(e)}")
            raise AuthError(f"Authentication failed: {str(e)}")

    @abstractmethod
    async def fetch_data(self) -> T:
        """Fetch data from the platform"""
        pass

    @abstractmethod
    def transform_response(
        self, response: Dict[str, Any], cache_info: Optional[Dict[str, Any]] = None
    ) -> T:
        """Transform raw API response into standardized format"""
        pass

    def with_retries(
        self,
        max_attempts: Optional[int] = None,
        base_delay: Optional[float] = None,
        max_delay: Optional[float] = None,
        retryable_exceptions: Optional[tuple] = None,
        retry_on_status_codes: Optional[set[int]] = None,
    ) -> Callable[[AsyncCallable], AsyncCallable]:
        """Retry decorator with exponential backoff and jitter

        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            retryable_exceptions: Tuple of exceptions to retry on
            retry_on_status_codes: Set of HTTP status codes to retry on

        Returns:
            Decorated async function with retry logic
        """

        def decorator(func: AsyncCallable) -> AsyncCallable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                config = self.retry_config
                attempts = max_attempts or config.max_attempts
                delay = base_delay or config.base_delay
                max_wait = max_delay or config.max_delay
                exceptions = retryable_exceptions or config.retryable_exceptions
                status_codes = retry_on_status_codes or config.retry_on_status_codes

                last_exception = None
                attempt = 0

                while attempt < attempts:
                    try:
                        response = await func(*args, **kwargs)

                        # Check status code for HTTP responses
                        if isinstance(response, httpx.Response):
                            if response.status_code in status_codes:
                                raise httpx.HTTPStatusError(
                                    f"HTTP {response.status_code}",
                                    request=response.request,
                                    response=response,
                                )
                        return response

                    except exceptions as e:
                        attempt += 1
                        last_exception = e

                        if attempt == attempts:
                            Logger.error(
                                f"Max retry attempts ({attempts}) reached for {func.__name__}"
                            )
                            raise last_exception

                        # Calculate delay with jitter
                        jitter_delay = min(
                            delay * (2 ** (attempt - 1)) + random.random(), max_wait
                        )

                        # Use retry-after header if available for rate limit errors
                        if (
                            isinstance(e, httpx.HTTPStatusError)
                            and e.response.status_code == 429
                            and "retry-after" in e.response.headers
                        ):
                            try:
                                jitter_delay = float(e.response.headers["retry-after"])
                            except (ValueError, TypeError):
                                pass

                        Logger.warning(
                            f"Attempt {attempt} failed for {func.__name__}, "
                            f"retrying in {jitter_delay:.2f}s: {str(e)}"
                        )
                        await asyncio.sleep(jitter_delay)

                    except Exception as e:
                        # Non-retryable exception
                        Logger.error(
                            f"Non-retryable error in {func.__name__}: {str(e)}"
                        )
                        raise

                raise last_exception

            return wrapper

        return decorator

    @with_retries()
    async def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        auth_required: bool = True,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None,
        invalidate_cache: bool = False,
    ) -> Dict[str, Any]:
        """Make an HTTP request with rate limiting, caching, and error handling"""
        # Check cache first
        cache_key = self._get_cache_key(method, url, params)
        cache_hit = False

        if use_cache and method.upper() == "GET":
            cached = await self._get_cached_response(cache_key)
            if cached:
                cache_hit = True
                cached["cache_info"] = {
                    "hit": True,
                    "key": cache_key,
                    "timestamp": datetime.now().isoformat(),
                }
                return cached

        # Acquire rate limit token
        await self.rate_limiter.acquire()

        try:
            # Add auth headers if required
            if auth_required:
                if not self.auth_state:
                    await self.authenticate()
                headers = headers or {}
                headers.update(self.auth_state.get_auth_header())

            response = await self.client.request(
                method=method, url=url, params=params, json=json, headers=headers
            )
            response.raise_for_status()
            result = response.json()

            # Add cache info
            result["cache_info"] = {
                "hit": cache_hit,
                "key": cache_key,
                "timestamp": datetime.now().isoformat(),
            }

            # Cache successful GET responses
            if use_cache and method.upper() == "GET":
                await self._cache_response(cache_key, result, cache_ttl)

            # Invalidate cache if requested
            if invalidate_cache:
                await self._invalidate_cache_patterns()

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                if auth_required and self.auth_state and self.auth_state.refresh_token:
                    # Try refreshing token
                    try:
                        self.auth_state = await self._refresh_auth_token()
                        await self._cache_auth(self.auth_state)
                        # Retry request with new token
                        return await self._make_request(
                            method,
                            url,
                            params,
                            json,
                            headers,
                            auth_required,
                            use_cache,
                            cache_ttl,
                            invalidate_cache,
                        )
                    except Exception as refresh_error:
                        Logger.error(f"Token refresh failed: {str(refresh_error)}")
                        raise RefreshTokenError("Token refresh failed")
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
