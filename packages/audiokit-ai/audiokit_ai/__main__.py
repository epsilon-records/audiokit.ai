"""Main entry point for AudioKit AI server."""
import uvicorn
from pathlib import Path
from .main import create_app
from .config import load_config

def app():
    """Run the FastAPI application."""
    # Load config from default location
    config = load_config(Path("config.yml"))
    
    # Create FastAPI app with config
    app = create_app()
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level=config.log_level
    )

if __name__ == "__main__":
    app() 