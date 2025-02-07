"""Authentication and authorization for AudioKit AI."""
from typing import Optional, Callable
from datetime import datetime, timedelta
import secrets
from fastapi import APIRouter, Depends, HTTPException, Security, status, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from audiokit_core.config import ServerConfig
import hashlib
from redis import RedisBackend
import semver
import asyncio
from .backends import MemoryBackend
from .exceptions import RateLimitExceededError
from .handlers import AuthHandler

# Create router
router = APIRouter(tags=["auth"])

class APIKey(BaseModel):
    """API key model."""
    key: str
    name: str
    enabled: bool = True
    rate_limit: int = 60  # requests per minute
    permissions: list[str] = ["analyze", "process"]
    created_at: datetime = datetime.utcnow()

class TokenData(BaseModel):
    """Token data with permissions."""
    key: str
    permissions: list[str]

# API key header
api_key_header = APIKeyHeader(name="X-API-Key")

# In-memory storage - replace with database in production
api_keys: dict[str, APIKey] = {}

class AuthHandler:
    def __init__(self, config: ServerConfig):
        self.version = "1.2.0"  # Added version tracking
        self.valid_keys = self._load_keys(config)
        self.security = APIKeyHeader(name="X-API-Key")
        self.rate_limiter = RateLimiter(config.redis_url)
        self.min_client_version = semver.VersionInfo.parse("1.2.0")
        self.key_rotation_interval = timedelta(days=7)
        self.last_rotation = datetime.utcnow()
        self._schedule_key_rotation()
        
        # Enhanced error responses
        self.error_responses = {
            401: {"description": "Invalid or missing API Key"},
            429: {"description": "Rate limit exceeded"},
            426: {"description": "Client upgrade required"},
            400: {"description": "Invalid version format"}
        }

    def _load_keys(self, config: ServerConfig) -> set:
        """Load and validate API keys from config"""
        if not config.api_keys:
            raise ValueError("No API keys configured")
        return {self._hash_key(k) for k in config.api_keys}

    def _hash_key(self, key: str) -> str:
        """Secure hash for API key storage"""
        return hashlib.sha256(key.encode()).hexdigest()

    def _validate_key(self, key: str) -> bool:
        """Validate against hashed keys"""
        return self._hash_key(key) in self.valid_keys

    async def api_key_auth(self, api_key: str = Depends(APIKeyHeader(name="X-API-Key"))) -> str:
        """Dependency for API key authentication with rate limiting"""
        if not self._validate_key(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API Key",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Check rate limits
        await self.rate_limiter.check_limit(api_key)
        return api_key

    def token_auth(self, token: str = Depends(APIKeyHeader(name="Authorization"))) -> str:
        """Dependency for token-based authentication"""
        if not self._validate_key(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API Key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token

    def create_scoped_validator(self, required_scope: str) -> Callable:
        """Factory method for creating scope-specific validators"""
        def validate_scope(api_key: str = Depends(self.api_key_auth)) -> str:
            # Implement scope validation logic here
            return api_key
        return validate_scope

    # Add version endpoint
    @router.get("/auth/version")
    async def get_auth_version(handler: AuthHandler = Depends()):
        return {"version": handler.version}

    async def validate_client_version(self, request: Request):
        """Validate client version from request headers"""
        version_header = request.headers.get("X-Client-Version")
        if not version_header:
            raise HTTPException(
                status_code=400,
                detail="Client version header required"
            )
            
        try:
            client_ver = semver.VersionInfo.parse(version_header)
            if client_ver < self.min_client_version:
                raise HTTPException(
                    status_code=426,
                    detail=f"Minimum client version {self.min_client_version} required"
                )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid version format"
            )

    # Add key rotation system
    async def rotate_keys(self):
        """Rotate API keys with zero-downtime"""
        new_keys = {
            self._hash_key(k.key): APIKey(
                **k.dict(),
                expires_at=datetime.utcnow() + timedelta(days=90)
            )
            for k in self.valid_keys.values()
            if k.expires_at > datetime.utcnow()
        }
        
        # Graceful transition period
        self.valid_keys.update(new_keys)
        self.last_rotation = datetime.utcnow()

    def _schedule_key_rotation(self):
        async def rotation_task():
            while True:
                await asyncio.sleep(self.key_rotation_interval.total_seconds())
                await self.rotate_keys()
                
        asyncio.create_task(rotation_task())

def init_api_keys(config: ServerConfig) -> AuthHandler:
    """Initialize authentication system with configuration"""
    return AuthHandler(config)

@router.post("/api-keys", response_model=APIKey)
async def create_api_key(name: str):
    """Create a new API key."""
    key = secrets.token_urlsafe(32)
    api_key = APIKey(key=key, name=name)
    api_keys[key] = api_key
    return api_key

class RateLimiter:
    def __init__(self, redis_url: Optional[str] = None):
        self.backend = RedisBackend(redis_url) if redis_url else MemoryBackend()
        
    async def check_rate_limit(self, key: str, limit: int) -> None:
        """Check rate limit using configured backend"""
        count = await self.backend.increment(key)
        if count > limit:
            raise RateLimitExceededError()

# Global rate limiter
rate_limiter = RateLimiter()

async def verify_token(api_key: str = Security(api_key_header)) -> str:
    """Verify API token.
    
    Args:
        api_key: API key from header
        
    Returns:
        Verified API key
        
    Raises:
        HTTPException: If authentication fails
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is required"
        )
    
    # Check if API key exists in allowed keys
    if api_key not in api_keys or not api_keys[api_key].enabled:
        raise HTTPException(
            status_code=401,
            detail="Invalid or disabled API key"
        )
    
    # If you need to check permissions, do it here
    # For now, all valid keys have access to all endpoints
    return api_key

@router.get("/auth/verify")
async def verify_auth(api_key: str = Depends(verify_token)):
    """Test endpoint for auth verification."""
    return {"message": "Authentication successful"}

def verify_permission(permission: str):
    """Create dependency to verify specific permission.
    
    Args:
        permission: Required permission
        
    Returns:
        Dependency function
    """
    async def verify(token: TokenData = Depends(verify_token)) -> TokenData:
        if permission not in token.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permission: {permission}"
            )
        return token
    return verify 