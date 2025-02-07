"""Main entry point for AudioKit AI server."""
import uvicorn
from fastapi import FastAPI
from pathlib import Path
from .app import create_app
from audiokit_core.config import load_config, AudioKitConfig
from audiokit_core.middleware import LoggingMiddleware

def get_config(config_path: Path = None) -> AudioKitConfig:
    """Get configuration with optional custom path"""
    return load_config(config_path or Path("config.yml"))

def create_and_configure_app(config: AudioKitConfig = None) -> FastAPI:
    """App factory with dependency injection"""
    app = create_app(config)
    
    # Add core middleware
    app.add_middleware(LoggingMiddleware, config=config)
    
    # Configure exception handlers
    from .exception_handlers import register_exception_handlers
    register_exception_handlers(app)
    
    return app

def run_server(app: FastAPI = None, config: AudioKitConfig = None):
    """Run the server with Uvicorn"""
    config = config or get_config()
    app = app or create_and_configure_app(config)
    
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower()
    )

if __name__ == "__main__":
    run_server() 