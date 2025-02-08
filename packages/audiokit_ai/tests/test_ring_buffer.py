"""Tests for RingBuffer implementation."""

import pytest
import numpy as np
from audiokit_ai.audio.ring_buffer import RingBuffer


@pytest.fixture
def buffer():
    """Create a test buffer."""
    return RingBuffer(size=16, channels=2)


def test_initialization():
    """Test buffer initialization."""
    # Should adjust to power of 2
    buf = RingBuffer(size=10, channels=1)
    assert buf.size == 16
    assert buf.channels == 1

    # Multi-channel
    buf = RingBuffer(size=16, channels=2)
    assert buf.size == 16
    assert buf.channels == 2


def test_write_read(buffer):
    """Test basic write and read operations."""
    # Write test data
    test_data = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
    written = buffer.write(test_data)
    assert written == 3

    # Read it back
    read_data = buffer.read(3)
    np.testing.assert_array_equal(test_data, read_data)


def test_wrap_around(buffer):
    """Test buffer wrapping behavior."""
    # Fill buffer
    data1 = np.ones((2, 14), dtype=np.float32)
    buffer.write(data1)

    # Read some data
    buffer.read(10)

    # Write more data (should wrap)
    data2 = np.full((2, 4), 2, dtype=np.float32)
    buffer.write(data2)

    # Read wrapped data
    result = buffer.read(8)
    np.testing.assert_array_equal(result[:, -4:], data2)


def test_overflow_underflow(buffer):
    """Test buffer overflow and underflow handling."""
    # Overflow
    data = np.ones((2, 20), dtype=np.float32)
    written = buffer.write(data)
    assert written == 16  # Should only write buffer size

    # Underflow
    buffer.read(10)
    empty = buffer.read(10)
    assert len(empty[0]) == 6  # Should only read available data


def test_peek(buffer):
    """Test peek operation."""
    test_data = np.array([[1, 2], [3, 4]], dtype=np.float32)
    buffer.write(test_data)

    # Peek should not advance read pointer
    peek1 = buffer.peek(2)
    peek2 = buffer.peek(2)
    np.testing.assert_array_equal(peek1, peek2)

    # Read should match peek
    read_data = buffer.read(2)
    np.testing.assert_array_equal(peek1, read_data)


def test_clear(buffer):
    """Test buffer clearing."""
    test_data = np.ones((2, 8), dtype=np.float32)
    buffer.write(test_data)
    buffer.clear()

    assert buffer.available_read == 0
    assert buffer.available_write == buffer.size


@pytest.mark.parametrize("size", [8, 16, 32])
def test_power_of_two(size):
    """Test power of 2 size adjustment."""
    buf = RingBuffer(size=size - 1, channels=1)
    assert buf.size == size

    buf = RingBuffer(size=size + 1, channels=1)
    assert buf.size == size * 2
