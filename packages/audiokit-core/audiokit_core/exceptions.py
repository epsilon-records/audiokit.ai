from fastapi import HTTPException

class AudioKitError(Exception):
    """Base exception class for all AudioKit errors"""
    
class AudioKitAPIError(AudioKitError):
    """Generic API error"""

class AudioKitAuthError(AudioKitAPIError):
    """Authentication failure"""

class AudioKitValidationError(AudioKitAPIError):
    """Invalid request parameters"""

class AudioKitRateLimitError(AudioKitAPIError):
    """Rate limit exceeded"""

class AudioKitServerError(AudioKitAPIError):
    """Server-side error"""

class AudioKitClientError(AudioKitAPIError):
    """Client-side error"""

class ConfigError(AudioKitError):
    """Configuration-related errors"""
    def __init__(self, detail: str):
        super().__init__(500, f"Configuration error: {detail}")

class ProcessingError(AudioKitError):
    """Audio processing errors"""
    def __init__(self, detail: str):
        super().__init__(400, f"Processing error: {detail}")

class AudioKitClientPackageError(AudioKitError):
    """Exception for AudioKit Client Package errors"""

class AudioKitClientPackageAuthError(AudioKitClientPackageError):
    """Exception for AudioKit Client Package authentication failures"""

class AudioKitClientPackageValidationError(AudioKitClientPackageError):
    """Exception for AudioKit Client Package input validation errors""" 