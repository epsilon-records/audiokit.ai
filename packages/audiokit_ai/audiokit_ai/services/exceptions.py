class AudioProcessingError(Exception):
    """Base class for audio processing errors"""

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
