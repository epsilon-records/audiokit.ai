"""Ring buffer implementation for real-time audio processing."""

from typing import Optional
import numpy as np
from loguru import logger


class RingBuffer:
    """Circular buffer optimized for real-time audio processing.

    A thread-safe ring buffer implementation that prevents memory leaks
    and provides zero-copy reads where possible.

    Attributes:
        size: Total buffer size in samples
        channels: Number of audio channels
        dtype: Numpy dtype for audio samples
    """

    def __init__(
        self,
        size: int,
        channels: int = 1,
        dtype: np.dtype = np.float32,
    ):
        """Initialize the ring buffer.

        Args:
            size: Buffer size in samples
            channels: Number of audio channels
            dtype: Data type for samples
        """
        if not (size & (size - 1) == 0):
            # Ensure size is power of 2 for efficient wrapping
            size = 1 << (size - 1).bit_length()
            logger.warning(f"Adjusting buffer size to power of 2: {size}")

        self.size = size
        self.channels = channels
        self.dtype = dtype

        # Initialize buffer
        self.buffer = np.zeros((channels, size), dtype=dtype)

        # Read/write pointers
        self._write_ptr = 0
        self._read_ptr = 0

        # For efficient wrapping
        self._wrap_mask = size - 1

        logger.debug(
            f"Initialized RingBuffer: size={size}, channels={channels}, dtype={dtype}"
        )

    @property
    def available_read(self) -> int:
        """Number of samples available for reading."""
        return (self._write_ptr - self._read_ptr) & self._wrap_mask

    @property
    def available_write(self) -> int:
        """Number of samples available for writing."""
        return self.size - self.available_read

    def write(self, data: np.ndarray) -> int:
        """Write data to the buffer.

        Args:
            data: Audio data to write (channels, samples)

        Returns:
            Number of samples written
        """
        if data.shape[0] != self.channels:
            raise ValueError(
                f"Channel mismatch: expected {self.channels}, got {data.shape[0]}"
            )

        # Calculate available space
        samples_to_write = min(len(data[0]), self.available_write)
        if samples_to_write == 0:
            logger.warning("Buffer full, no samples written")
            return 0

        # Calculate write positions
        write_end = (self._write_ptr + samples_to_write) & self._wrap_mask
        if write_end > self._write_ptr:
            # Continuous write
            self.buffer[:, self._write_ptr : write_end] = data[:, :samples_to_write]
        else:
            # Split write
            first_part = self.size - self._write_ptr
            self.buffer[:, self._write_ptr :] = data[:, :first_part]
            self.buffer[:, :write_end] = data[:, first_part:samples_to_write]

        self._write_ptr = write_end
        return samples_to_write

    def read(self, size: Optional[int] = None, advance: bool = True) -> np.ndarray:
        """Read data from the buffer.

        Args:
            size: Number of samples to read (None = all available)
            advance: Whether to advance read pointer

        Returns:
            Array of read samples (channels, samples)
        """
        available = self.available_read
        if size is None:
            size = available
        samples_to_read = min(size, available)

        if samples_to_read == 0:
            logger.warning("Buffer empty, returning zeros")
            return np.zeros((self.channels, 0), dtype=self.dtype)

        # Calculate read positions
        read_end = (self._read_ptr + samples_to_read) & self._wrap_mask
        if read_end > self._read_ptr:
            # Continuous read
            data = self.buffer[:, self._read_ptr : read_end].copy()
        else:
            # Split read
            data = np.empty((self.channels, samples_to_read), dtype=self.dtype)
            first_part = self.size - self._read_ptr
            data[:, :first_part] = self.buffer[:, self._read_ptr :]
            data[:, first_part:] = self.buffer[:, :read_end]

        if advance:
            self._read_ptr = read_end

        return data

    def peek(self, size: Optional[int] = None) -> np.ndarray:
        """Read without advancing read pointer."""
        return self.read(size, advance=False)

    def clear(self) -> None:
        """Reset buffer to empty state."""
        self._write_ptr = 0
        self._read_ptr = 0
        self.buffer.fill(0)
        logger.debug("Buffer cleared")
