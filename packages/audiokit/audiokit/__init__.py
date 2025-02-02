"""AudioKit: Open-source SDK for music platform integrations.

A powerful and flexible toolkit for working with music platforms and audio processing.

Example:
    >>> from audiokit import AudioKit
    >>> client = AudioKit()
    >>> track = client.load_track("path/to/audio.wav")
    >>> track.play()

For more examples, see the documentation at https://docs.audiokit.org
"""

__version__ = "1.0.0"

from .core import AudioKit, Track, AudioData
from .logger import setup_logger

__all__ = [
    "AudioKit",
    "Track",
    "AudioData",
    "setup_logger",
]
