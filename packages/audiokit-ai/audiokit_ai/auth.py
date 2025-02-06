"""Authentication and authorization for AudioKit AI service."""
from typing import Optional, Dict
import time
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from fastapi import Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel

from . import errors

logger = logging.getLogger(__name__)

# Configuration (should be moved to environment variables)
JWT_SECRET = "your-secret-key"  # TODO: Move to env
JWT_ALGORITHM = "HS256"
API_KEYS = {
    "test-key": {
        "client_id": "test-client",
        "rate_limit": 100,  # requests per minute
        "permissions": ["analyze", "generate"]
    }
}

class TokenData(BaseModel):
    """JWT token data."""
    client_id: str
    permissions: list[str]
    exp: datetime

class RateLimit:
    """Rate limiting implementation."""
    def __init__(self):
        self.requests: Dict[str, list[float]] = {}
    
    def check_rate_limit(self, client_id: str, limit: int) -> None:
        """Check if client has exceeded rate limit.
        
        Args:
            client_id: Client identifier
            limit: Maximum requests per minute
            
        Raises:
            RateLimitError: If rate limit is exceeded
        """
        now = time.time()
        minute_ago = now - 60
        
        # Initialize or clean old requests
        if client_id not in self.requests:
            self.requests[client_id] = []
        self.requests[client_id] = [t for t in self.requests[client_id] if t > minute_ago]
        
        # Check limit
        if len(self.requests[client_id]) >= limit:
            retry_after = int(60 - (now - self.requests[client_id][0]))
            raise errors.RateLimitError(retry_after)
            
        # Add request
        self.requests[client_id].append(now)

rate_limiter = RateLimit()
security = HTTPBearer()

async def verify_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Verify API key and return token data.
    
    Args:
        request: FastAPI request
        credentials: Bearer token credentials
        
    Returns:
        TokenData containing client information
        
    Raises:
        InvalidAPIKeyError: If API key is invalid
    """
    try:
        api_key = credentials.credentials
        
        # Verify API key exists
        if api_key not in API_KEYS:
            raise errors.InvalidAPIKeyError()
            
        client_data = API_KEYS[api_key]
        
        # Check rate limit
        rate_limiter.check_rate_limit(
            client_data["client_id"],
            client_data["rate_limit"]
        )
        
        # Create JWT token
        token_data = TokenData(
            client_id=client_data["client_id"],
            permissions=client_data["permissions"],
            exp=datetime.utcnow() + timedelta(minutes=15)
        )
        
        # Log access
        logger.info(
            f"API access: {request.method} {request.url.path}",
            extra={
                "client_id": token_data.client_id,
                "ip": request.client.host
            }
        )
        
        return token_data
        
    except jwt.PyJWTError:
        raise errors.InvalidAPIKeyError()
    except errors.RateLimitError as e:
        raise e
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise errors.InvalidAPIKeyError()

def verify_permission(permission: str):
    """Dependency to verify specific permission.
    
    Args:
        permission: Required permission
        
    Returns:
        Dependency function
    """
    async def verify(token: TokenData = Depends(verify_api_key)) -> None:
        if permission not in token.permissions:
            raise errors.InvalidAPIKeyError()
    return verify 