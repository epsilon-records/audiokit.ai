# CONFIDENTIAL AND PROPRIETARY
#
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
#
# This software is confidential and proprietary.
#

#
# This file is part of the AudioKit AI package.
#

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from dotenv import load_dotenv
from audiokit_ai.core.logger import logger
from audiokit_ai.api.endpoints import router as api_router

# Ensure correct torchaudio imports are used

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
app.include_router(api_router, prefix="/api/v1")

load_dotenv()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
