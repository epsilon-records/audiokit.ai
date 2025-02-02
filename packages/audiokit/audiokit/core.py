"""Core AudioKit functionality.

This module provides the main AudioKit class and related data structures
for audio processing and manipulation.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class AudioData:
    """Container for audio data with metadata.

    Args:
        sample_rate: Sample rate in Hz
        channels: Number of audio channels
        duration: Duration in seconds
        data: Raw audio data
    """

    sample_rate: int
    channels: int
    duration: float
    data: bytes

    def __post_init__(self):
        """Validate audio data after initialization."""
        if self.sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        if self.channels <= 0:
            raise ValueError("Number of channels must be positive")
        if self.duration < 0:
            raise ValueError("Duration cannot be negative")


class Track:
    """Represents a single audio track.

    Args:
        path: Path to audio file
        audio_data: Processed audio data
    """

    def __init__(self, path: Union[str, Path], audio_data: Optional[AudioData] = None):
        self.path = Path(path)
        self.audio_data = audio_data
        self._validate_path()

    def _validate_path(self):
        """Ensure the audio file exists and is readable."""
        if not self.path.exists():
            raise FileNotFoundError(f"Audio file not found: {self.path}")
        if not self.path.is_file():
            raise ValueError(f"Path is not a file: {self.path}")

    def play(self):
        """Play the audio track.

        Returns:
            None

        Raises:
            RuntimeError: If audio data is not loaded
        """
        if not self.audio_data:
            raise RuntimeError("No audio data loaded")
        logger.info(f"Playing track: {self.path}")
        # TODO: Implement actual audio playback
        print(f"Playing {self.path} (Sample rate: {self.audio_data.sample_rate}Hz)")


class AudioKit:
    """Main class for audio processing functionality.

    Example:
        >>> client = AudioKit()
        >>> track = client.load_track("song.wav")
        >>> track.play()
    """

    def __init__(self):
        """Initialize AudioKit with default settings."""
        logger.info("Initializing AudioKit")

    def load_track(self, path: Union[str, Path]) -> Track:
        """Load an audio track from file.

        Args:
            path: Path to audio file

        Returns:
            Track object with loaded audio data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid
        """
        logger.info(f"Loading track from {path}")

        # Create dummy audio data for example
        audio_data = AudioData(sample_rate=44100, channels=2, duration=0.0, data=b"")

        return Track(path, audio_data)
