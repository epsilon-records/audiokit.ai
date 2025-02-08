# Audio Buffer API

!!! note "Documentation Needed"
    This page is a placeholder. API documentation needs to be generated.

## Overview

The AudioBuffer class provides the core data structure for audio processing in AudioKit.

## Class Reference

```python
class AudioBuffer:
    def __init__(self, channels: int, size: int):
        """Initialize an audio buffer.
        
        Args:
            channels: Number of audio channels
            size: Buffer size in samples
        """
        pass
```

## Examples

```python
from audiokit import AudioBuffer

# Create a stereo buffer
buffer = AudioBuffer(channels=2, size=1024)

# Process the buffer
processed = effects_chain.process(buffer)
```

## Methods

- `get_channel(channel: int) -> ndarray`
- `set_channel(channel: int, data: ndarray)`
- `clear()`
- `copy() -> AudioBuffer`

## Properties

- `channels: int`
- `size: int`
- `sample_rate: float`
- `duration: float` 