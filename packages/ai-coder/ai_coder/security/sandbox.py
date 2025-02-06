from typing import Optional
from pathlib import Path
import os
from functools import wraps

class SecurityViolation(Exception):
    """Raised when a security boundary is violated."""
    pass

class Sandbox:
    """Provides a secure sandbox for file operations."""
    
    def __init__(self, root_dir: Path):
        """Initialize sandbox with root directory."""
        self.root_dir = root_dir.resolve()
        
    def validate_path(self, path: Path) -> Path:
        """Validate if path is within sandbox.
        
        Args:
            path: Path to validate
            
        Returns:
            Resolved path if valid
            
        Raises:
            SecurityViolation: If path is outside sandbox
        """
        try:
            resolved_path = path.resolve()
            if not str(resolved_path).startswith(str(self.root_dir)):
                raise SecurityViolation(
                    f"Access denied: {path} is outside sandbox root {self.root_dir}"
                )
            return resolved_path
        except Exception as e:
            raise SecurityViolation(f"Invalid path: {str(e)}")
            
    def safe_open(self, path: Path, mode: str = 'r') -> Optional[Path]:
        """Safely open a file within sandbox.
        
        Args:
            path: Path to file
            mode: File open mode
            
        Returns:
            File handle if successful
            
        Raises:
            SecurityViolation: If operation is not allowed
        """
        if 'w' in mode or 'a' in mode:
            # Create parent directories if needed
            parent = path.parent
            if not parent.exists():
                if not str(parent.resolve()).startswith(str(self.root_dir)):
                    raise SecurityViolation(
                        f"Cannot create directory outside sandbox: {parent}"
                    )
                parent.mkdir(parents=True, exist_ok=True)
                
        resolved_path = self.validate_path(path)
        return resolved_path

def sandbox_required(f):
    """Decorator to enforce sandbox boundaries."""
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'sandbox'):
            raise SecurityViolation("Sandbox not initialized")
        return f(self, *args, **kwargs)
    return wrapper 