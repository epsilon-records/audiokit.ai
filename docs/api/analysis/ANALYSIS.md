# Audio Analysis API

!!! note "Documentation Needed"
    This page is a placeholder. API documentation needs to be generated.

## Overview

The analysis module provides tools for analyzing audio signals and extracting features.

## Analyzers

### Spectral Analysis
- FFT Analyzer
- Spectrogram
- Mel-Frequency Analysis

### Time Domain Analysis
- RMS Level
- Peak Detection
- Zero Crossing Rate

### Feature Extraction
- Pitch Detection
- Onset Detection
- Beat Detection

## Example Usage

```python
from audiokit.analysis import SpectralAnalyzer

# Create an analyzer
analyzer = SpectralAnalyzer(fft_size=2048)

# Analyze audio buffer
spectrum = analyzer.analyze(buffer)

# Get frequency peaks
peaks = spectrum.find_peaks(threshold=-60)

# Get specific metrics
frequency = peaks[0].frequency
magnitude = peaks[0].magnitude
```

## Base Classes

- `Analyzer`: Base class for all analyzers
- `SpectralAnalyzer`: Base class for frequency domain analysis
- `TimeAnalyzer`: Base class for time domain analysis
- `FeatureExtractor`: Base class for feature extraction 