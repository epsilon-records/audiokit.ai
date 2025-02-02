"""Base Platform Integration Framework.

This module provides the foundation for integrating with various music and social media
platforms. It implements core functionality for authentication, rate limiting,
caching, and error handling that all platform integrations build upon.

Key Features:
    - Rate limiting with configurable thresholds
    - Token-based authentication with automatic refresh
    - Redis-based response caching
    - Retry mechanism with exponential backoff
    - Standardized error handling

Performance:
    - Async/await for non-blocking I/O
    - Efficient cache key generation
    - Optimized rate limiting algorithm
    - Connection pooling for HTTP requests

Example:
    >>> class SpotifyProcessor(PlatformProcessor[SpotifyResponse]):
    ...     async def fetch_data(self) -> SpotifyResponse:
    ...         data = await self._make_request("GET", "/v1/me/tracks")
    ...         return self.transform_response(data)

Note:
    All platform-specific processors should inherit from PlatformProcessor
    and implement the required abstract methods.
"""

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
    """Rate limiter for API requests with sliding window algorithm.

    This class implements a sliding window rate limiter to prevent
    exceeding API rate limits. It maintains a list of request timestamps
    and enforces waiting periods when limits are reached.

    Args:
        requests_per_minute: Maximum number of requests allowed per minute

    Performance:
        - O(1) token acquisition
        - O(n) cleanup where n is requests in window
        - Memory usage proportional to requests_per_minute

    Example:
        >>> limiter = RateLimiter(requests_per_minute=60)
        >>> await limiter.acquire()  # Waits if limit reached
    """

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.time_window = 60  # seconds
        self.requests = []

    async def acquire(self):
        """Acquire a rate limit token, waiting if necessary.

        This method implements the core rate limiting logic:
        1. Removes expired requests from the window
        2. Checks if current request would exceed limit
        3. Waits if necessary before allowing request
        4. Records the new request timestamp

        Raises:
            RateLimitError: If rate limit is exceeded and retry fails

        Performance:
            - O(n) cleanup of expired requests
            - O(1) limit check and token grant
        """
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
    """Base exception for platform-related errors.

    All platform-specific exceptions should inherit from this class
    to enable consistent error handling across the application.
    """

    pass


class AuthError(PlatformError):
    """Authentication-related errors.

    Raised when authentication fails, including invalid credentials,
    expired tokens, and failed refresh attempts.
    """

    pass


class RateLimitError(PlatformError):
    """Rate limit exceeded errors.

    Raised when platform rate limits are exceeded and retry
    attempts have been exhausted.
    """

    pass


class TokenExpiredError(AuthError):
    """Token expired error.

    Raised when an access token has expired and needs to be
    refreshed before continuing.
    """

    pass


class RefreshTokenError(AuthError):
    """Token refresh error.

    Raised when attempting to refresh an access token fails,
    requiring re-authentication.
    """

    pass


class CacheConfig(BaseModel):
    """Cache configuration for platform responses.

    Defines caching behavior including TTL, key prefixes,
    and invalidation patterns.

    Attributes:
        enabled: Whether caching is enabled
        ttl: Time-to-live in seconds for cached items
        prefix: Cache key prefix for namespace isolation
        namespace: Optional sub-namespace for further isolation
        invalidation_patterns: Patterns for cache invalidation

    Example:
        >>> config = CacheConfig(
        ...     ttl=3600,
        ...     prefix="spotify",
        ...     namespace="user_123",
        ...     invalidation_patterns=["playlists*"]
        ... )
    """

    enabled: bool = True
    ttl: int = 3600  # 1 hour default
    prefix: str = "platform"
    namespace: Optional[str] = None
    invalidation_patterns: list[str] = Field(default_factory=list)


class ResponseModel(BaseModel):
    """Base model for standardized platform responses.

    All platform-specific response models should inherit from this
    to ensure consistent response structure.

    Attributes:
        platform: Name of the platform (e.g., "spotify", "youtube")
        timestamp: When the response was received
        raw_data: Original platform response data
        cache_info: Optional caching metadata

    Example:
        >>> response = ResponseModel(
        ...     platform="spotify",
        ...     raw_data={"tracks": []},
        ...     cache_info={"hit": True, "ttl": 3600}
        ... )
    """

    platform: str
    timestamp: datetime = Field(default_factory=datetime.now)
    raw_data: Dict[str, Any]
    cache_info: Optional[Dict[str, Any]] = None


class AuthState(BaseModel):
    """Platform authentication state.

    Manages authentication tokens and their lifecycle.

    Attributes:
        access_token: The current access token
        refresh_token: Optional token for refreshing access
        token_type: Token type (e.g., "Bearer")
        expires_at: When the access token expires
        scopes: List of granted permission scopes

    Example:
        >>> auth = AuthState(
        ...     access_token="xyz",
        ...     refresh_token="abc",
        ...     expires_at=datetime.now() + timedelta(hours=1)
        ... )
    """

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    scopes: list[str] = Field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        """Check if the access token is expired.

        Returns:
            bool: True if token is expired or will expire soon

        Note:
            Adds a small buffer before actual expiration to prevent
            edge cases with nearly-expired tokens.
        """
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at

    def get_auth_header(self) -> Dict[str, str]:
        """Get the authorization header for API requests.

        Returns:
            Dict containing the Authorization header

        Example:
            >>> headers = auth_state.get_auth_header()
            >>> headers
            {'Authorization': 'Bearer xyz123'}
        """
        return {"Authorization": f"{self.token_type} {self.access_token}"}


T = TypeVar("T", bound=ResponseModel)


class RetryConfig(BaseModel):
    """Configuration for request retry mechanism.

    Defines retry behavior including delays, exceptions to retry on,
    and status codes that should trigger retries.

    Attributes:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        retryable_exceptions: Exception types to retry on
        retry_on_status_codes: HTTP status codes to retry on

    Example:
        >>> config = RetryConfig(
        ...     max_attempts=5,
        ...     base_delay=1.0,
        ...     max_delay=30.0
        ... )
    """

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
    """Base class for all platform data processors.

    This abstract class provides the foundation for platform-specific
    processors, implementing common functionality for authentication,
    rate limiting, caching, and error handling.

    Type Parameters:
        T: Response model type, must inherit from ResponseModel

    Attributes:
        artist_data: Artist data being processed
        rate_limiter: Rate limiting implementation
        client: HTTP client for API requests
        auth_state: Current authentication state
        redis: Redis client for caching
        cache_config: Caching configuration
        retry_config: Retry mechanism configuration

    Example:
        >>> class SpotifyProcessor(PlatformProcessor[SpotifyResponse]):
        ...     async def fetch_data(self) -> SpotifyResponse:
        ...         return await self._make_request("GET", "/v1/me")
    """

    def __init__(self, artist_data: ArtistData):
        """Initialize the platform processor.

        Args:
            artist_data: Artist data to process

        Note:
            Sets up HTTP client, rate limiter, and cache connection.
            Subclasses should call super().__init__() first.
        """
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
        """Async context manager entry.

        Returns:
            self: The processor instance

        Example:
            >>> async with SpotifyProcessor(artist_data) as proc:
            ...     await proc.process()
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit.

        Ensures proper cleanup of resources including HTTP client
        and Redis connection.
        """
        await self.client.aclose()
        await self.redis.close()

    def _get_cache_key(
        self, method: str, url: str, params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a unique cache key for the request.

        Args:
            method: HTTP method
            url: Request URL
            params: Optional query parameters

        Returns:
            str: SHA-256 hash of the request parameters

        Note:
            Includes namespace in key generation to prevent collisions
        """
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
        """Retrieve a cached response.

        Args:
            key: Cache key to look up

        Returns:
            Optional[Dict[str, Any]]: Cached response if found

        Note:
            Returns None if caching is disabled or on cache miss
        """
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
        """Cache a response.

        Args:
            key: Cache key
            response: Response data to cache
            ttl: Optional TTL override

        Note:
            Uses configured TTL if not overridden
        """
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
        """Invalidate cache entries matching configured patterns.

        This method is useful for clearing related cache entries
        when data is updated. For example, clearing all playlist
        caches when a track is added.

        Note:
            Patterns are prefixed with the configured cache prefix
        """
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
        """Get platform-specific authentication credentials.

        Returns:
            Dict[str, Any]: Credentials needed for authentication

        Note:
            Implementation should handle secure credential retrieval
        """
        pass

    @abstractmethod
    async def _refresh_auth_token(self) -> AuthState:
        """Refresh the authentication token.

        Returns:
            AuthState: New authentication state

        Raises:
            RefreshTokenError: If token refresh fails
        """
        pass

    async def _get_cached_auth(self) -> Optional[AuthState]:
        """Get cached authentication state.

        Returns:
            Optional[AuthState]: Cached auth state if found

        Note:
            Auth state is cached per artist and platform
        """
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
        """Cache authentication state.

        Args:
            auth: Authentication state to cache
            ttl: Optional TTL override

        Note:
            Uses token expiration time as TTL if not overridden
        """
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
