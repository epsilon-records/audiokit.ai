"""Server management functionality for AudioKit AI."""
import uvicorn
from pathlib import Path
import sys
from typing import Optional

def start_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    config: Optional[Path] = None
) -> None:
    """Start the AudioKit AI server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload
        config: Path to config file
    """
    uvicorn.run(
        "audiokit_ai.main:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
        reload_dirs=["audiokit_ai"] if reload else None
    )

if __name__ == "__main__":
    start_server() 