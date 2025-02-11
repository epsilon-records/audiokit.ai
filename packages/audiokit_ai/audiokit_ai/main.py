# CONFIDENTIAL AND PROPRIETARY
#
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
#
# This software is confidential and proprietary.
#

#
# This file is part of the AudioKit AI package.
#

import multiprocessing
import os
import sys

import redis.asyncio as redis
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter

from audiokit_ai.api.endpoints import router, socket_app
from audiokit_ai.core.logger import logger

from .core.config import settings


# Keep in main.py to ensure proper initialization order
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["XLA_PYTHON_CLIENT_ALLOCATOR"] = "platform"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Then load dotenv
load_dotenv()

# Ensure correct torchaudio imports are used


def create_application() -> FastAPI:
    """Factory function for creating the configured FastAPI application"""
    app = FastAPI(
        title="AudioKit AI",
        version="1.3.0",
        description="Core API service for AudioKit AI processing pipeline",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # Enable CORS (adjust origins as needed)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add/modify the logger configuration near the top of the file
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level.icon} {level}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # Initialize rate limiter using Redis on startup
    @app.on_event("startup")
    async def startup():
        redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=0,
            decode_responses=True,
        )
        await FastAPILimiter.init(redis_client)

        # Add process monitoring
        multiprocessing.set_start_method("spawn", force=True)
        logger.info(
            f"Initialized multiprocessing with {multiprocessing.cpu_count()} cores",
        )

    # Include API endpoints
    app.include_router(router, prefix="/api/v1")

    # Mount Socket.IO server
    app.mount("/socket.io", socket_app)

    return app


# Create the application instance
app = create_application()


@app.on_event("startup")
async def startup_event():
    """Initialize application services on startup"""
    logger.info("🚀 Starting AudioKit AI service...")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    logger.info("🛑 Shutting down AudioKit AI service...")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Add process health check
    if request.url.path == "/api/v1/health":
        return JSONResponse(
            {"status": "ok", "workers": len(multiprocessing.active_children())},
        )

    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
