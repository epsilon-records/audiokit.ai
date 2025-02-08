# Audio Effects API

!!! note "Documentation Needed"
    This page is a placeholder. API documentation needs to be generated.

## Overview

The effects module provides a collection of audio processing effects that can be chained together.

## Available Effects

### Dynamics
- Compressor
- Limiter
- Gate

### Time-Based
- Delay
- Reverb
- Chorus

### Filters
- EQ
- Low Pass
- High Pass
- Band Pass

### Modulation
- Phaser
- Flanger
- Tremolo

## Effect Chain

```python
from audiokit.effects import Reverb, Delay, Compressor

# Create an effects chain
chain = [
    Reverb(room_size=0.8, damping=0.5),
    Delay(time=0.3, feedback=0.4),
    Compressor(threshold=-20, ratio=4.0)
]

# Process audio through the chain
for effect in chain:
    buffer = effect.process(buffer)
```

## Base Classes

- `Effect`: Base class for all effects
- `TimeBasedEffect`: Base class for time-based effects
- `DynamicsEffect`: Base class for dynamics processors
- `FilterEffect`: Base class for filters 