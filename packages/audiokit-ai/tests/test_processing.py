import pytest
import numpy as np
from audiokit_ai.processing import process_audio
from audiokit_ai.models import AudioAnalysis

@pytest.mark.asyncio
async def test_process_audio_valid():
    # Create a simple sine wave
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = (np.sin(2 * np.pi * 440.0 * t) * 32767).astype(np.int16)
    
    result = await process_audio(audio_data.tobytes())
    assert isinstance(result, AudioAnalysis)
    assert result.duration == pytest.approx(duration, 0.01)
    assert result.sample_rate == sample_rate

@pytest.mark.asyncio
async def test_process_audio_invalid():
    with pytest.raises(Exception):
        await process_audio(b"invalid audio data") 