import pytest
import numpy as np
import soundfile as sf
import io
import base64
from audiokit_ai.services.processing import auto_master
from fastapi import UploadFile


@pytest.fixture
def test_audio_files(tmp_path):
    """Create temporary target and reference audio files for testing."""
    # Create a target audio file (sine wave)
    target_path = tmp_path / "target.wav"
    sr = 44100
    t = np.linspace(0, 1, sr)
    target_audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    sf.write(target_path, target_audio, sr)

    # Create a reference audio file (different sine wave)
    reference_path = tmp_path / "reference.wav"
    reference_audio = 0.8 * np.sin(2 * np.pi * 880 * t)
    sf.write(reference_path, reference_audio, sr)

    return target_path, reference_path


@pytest.mark.asyncio
async def test_auto_master(test_audio_files):
    """Test the auto_master function."""
    target_path, reference_path = test_audio_files

    # Create UploadFile objects
    with open(target_path, "rb") as f:
        target_file = UploadFile(file=f, filename="target.wav")
    with open(reference_path, "rb") as f:
        reference_file = UploadFile(file=f, filename="reference.wav")

    # Call the auto_master function
    result = await auto_master(target_file, reference_file)

    # Verify the result is a base64-encoded string
    assert isinstance(result, str)
    assert len(result) > 0

    # Decode the result and verify it's valid WAV audio
    decoded = base64.b64decode(result)
    audio, sr = sf.read(io.BytesIO(decoded))
    assert sr == 44100
    assert len(audio) > 0
