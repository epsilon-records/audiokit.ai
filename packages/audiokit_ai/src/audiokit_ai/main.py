from fastapi import FastAPI, WebSocket, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from .api import endpoints
from .core.config import settings
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis

app = FastAPI(title="AudioKit-AI Server")

# Enable CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize rate limiter using Redis on startup
@app.on_event("startup")
async def startup():
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        decode_responses=True,
    )
    await FastAPILimiter.init(redis_client)

# Include API endpoints
app.include_router(endpoints.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_token(token: str = Depends(oauth2_scheme)):
    # Your token verification logic here
    return {} 