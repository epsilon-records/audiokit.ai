"""Authentication and authorization for AudioKit AI."""
from typing import Optional
from datetime import datetime, timedelta
import secrets
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

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

def init_api_keys(config):
    """Initialize API keys from config."""
    # Get API key from config, fallback to test-key if not present
    test_key = getattr(config, 'api_key', 'test-key')
    
    # Clear existing keys
    api_keys.clear()
    
    # Add the configured key
    api_keys[test_key] = APIKey(
        key=test_key,
        name="Default Key",
        enabled=True,
        permissions=["analyze", "process"]
    )
    return test_key

@router.post("/api-keys", response_model=APIKey)
async def create_api_key(name: str):
    """Create a new API key."""
    key = secrets.token_urlsafe(32)
    api_key = APIKey(key=key, name=name)
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