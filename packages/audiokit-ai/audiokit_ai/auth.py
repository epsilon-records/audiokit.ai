"""Authentication and authorization for AudioKit AI."""
from typing import Optional
from datetime import datetime, timedelta
import secrets
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

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

# In-memory store for API keys (replace with database in production)
api_keys: dict[str, APIKey] = {}

# API key header
api_key_header = APIKeyHeader(name="X-API-Key")

def create_api_key(name: str, permissions: Optional[list[str]] = None) -> APIKey:
    """Create new API key.
    
    Args:
        name: Name/description for the key
        permissions: Optional list of permissions
        
    Returns:
        Created API key
    """
    key = secrets.token_urlsafe(32)
    api_key = APIKey(
        key=key,
        name=name,
        permissions=permissions or ["analyze", "process"]
    )
    api_keys[key] = api_key
    return api_key

class RateLimiter:
    """Rate limiting implementation."""
    def __init__(self):
        self._requests: dict[str, list[datetime]] = {}
        
    def check_rate_limit(self, key: str, limit: int) -> None:
        """Check if key has exceeded rate limit.
        
        Args:
            key: API key to check
            limit: Maximum requests per minute
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        if key in self._requests:
            self._requests[key] = [
                t for t in self._requests[key] 
                if t > minute_ago
            ]
        else:
            self._requests[key] = []
            
        # Check limit
        if len(self._requests[key]) >= limit:
            retry_after = 60 - int((now - self._requests[key][0]).total_seconds())
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(retry_after)}
            )
            
        # Add request
        self._requests[key].append(now)

# Global rate limiter
rate_limiter = RateLimiter()

async def verify_api_key(
    api_key: str = Security(api_key_header)
) -> TokenData:
    """Verify API key and rate limit.
    
    Args:
        api_key: API key from request header
        
    Returns:
        Token data with permissions
        
    Raises:
        HTTPException: If key is invalid or rate limit exceeded
    """
    if api_key not in api_keys:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
        
    key_data = api_keys[api_key]
    if not key_data.enabled:
        raise HTTPException(
            status_code=401,
            detail="API key is disabled"
        )
        
    # Check rate limit
    rate_limiter.check_rate_limit(api_key, key_data.rate_limit)
    
    return TokenData(
        key=api_key,
        permissions=key_data.permissions
    )

def verify_permission(permission: str):
    """Create dependency to verify specific permission.
    
    Args:
        permission: Required permission
        
    Returns:
        Dependency function
    """
    async def verify(token: TokenData = Depends(verify_api_key)) -> TokenData:
        if permission not in token.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permission: {permission}"
            )
        return token
    return verify 