from fastapi import HTTPException

class AudioKitError(HTTPException):
    """Base exception for AudioKit errors"""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        self.type = self.__class__.__name__

class ConfigError(AudioKitError):
    """Configuration-related errors"""
    def __init__(self, detail: str):
        super().__init__(500, f"Configuration error: {detail}")

class ProcessingError(AudioKitError):
    """Audio processing errors"""
    def __init__(self, detail: str):
        super().__init__(400, f"Processing error: {detail}")

class AudioKitAPIError(AudioKitError):
    """Exception for API communication errors"""

class AudioKitAuthError(AudioKitError):
    """Exception for authentication failures"""

class AudioKitValidationError(AudioKitError):
    """Exception for input validation errors""" 