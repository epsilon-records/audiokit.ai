"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .knowledge import router as knowledge_router
from ..logger import Logger
from config import cfg


app = FastAPI(
    title="AudioKit API",
    description="API for AudioKit platform services",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
app.include_router(knowledge_router)


@app.on_event("startup")
async def startup():
    """Startup event handler"""
    Logger.info("Starting AudioKit API")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler"""
    Logger.info("Shutting down AudioKit API")
