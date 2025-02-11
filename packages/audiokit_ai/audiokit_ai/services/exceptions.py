class AudioProcessingError(Exception):
    """Base class for audio processing exceptions"""

    status_code = 500


class InvalidAudioFormatError(AudioProcessingError):
    """Raised when audio format is invalid"""

    status_code = 400


class FileTooLargeError(AudioProcessingError):
    """Raised when file size exceeds limit"""

    status_code = 413


class InsufficientMemoryError(AudioProcessingError):
    """Raised when system memory is insufficient"""

    status_code = 507


class ResourceError(AudioProcessingError):
    """Raised when system resources are unavailable"""

    status_code = 503


class ProcessingError(AudioProcessingError):
    """Raised when audio processing fails"""

    status_code = 500
