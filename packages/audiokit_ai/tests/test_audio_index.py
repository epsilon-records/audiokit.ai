import pytest
import numpy as np
from audiokit_ai.index.audio_index import AudioIndex
from unittest.mock import patch
import os


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(
        os.environ,
        {
            "TESTING": "true",
            "MOCK_SERVICES": "true",
            "PINECONE_API_KEY": "fake-key",
            "PINECONE_ENVIRONMENT": "test",
            "GOOGLE_APPLICATION_CREDENTIALS": "fake-path",
        },
    ):
        yield


@pytest.fixture
def mock_services():
    """Mock external services."""
    with patch("google.cloud.speech_v1p1beta1.SpeechClient"), patch(
        "llama_index.VectorIndex"
    ), patch("pinecone.init"), patch("pinecone.Index"):
        yield


@pytest.fixture
def audio_index(tmp_path):
    """Create a test audio index."""
    return AudioIndex(persist_dir=str(tmp_path / "test_index"))


def test_add_audio(audio_index, tmp_path):
    """Test adding audio to the index."""
    # Create test audio file
    audio_path = str(tmp_path / "test.wav")
    sample_rate = 44100
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave

    # Save as WAV
    import soundfile as sf

    sf.write(audio_path, audio, sample_rate)

    # Add to index
    audio_id = audio_index.add_audio(
        audio_path, metadata={"type": "test", "frequency": 440}
    )

    assert audio_id == "test.wav"


def test_search(audio_index, tmp_path):
    """Test searching the index."""
    # Add test audio
    audio_path = str(tmp_path / "test.wav")
    sample_rate = 44100
    t = np.linspace(0, 2.0, int(sample_rate * 2.0))
    audio = np.sin(2 * np.pi * 440 * t)
    import soundfile as sf

    sf.write(audio_path, audio, sample_rate)

    audio_id = audio_index.add_audio(audio_path)

    # Test text search
    results = audio_index.search("sine wave", n_results=1)
    assert len(results) == 1
    assert results[0]["id"] == audio_id

    # Test audio similarity search
    results = audio_index.search(audio_path, n_results=1)
    assert len(results) == 1
    assert results[0]["id"] == audio_id


def test_delete(audio_index, tmp_path):
    """Test deleting from the index."""
    # Add and then delete audio
    audio_path = str(tmp_path / "test.wav")
    sample_rate = 44100
    t = np.linspace(0, 2.0, int(sample_rate * 2.0))
    audio = np.sin(2 * np.pi * 440 * t)
    import soundfile as sf

    sf.write(audio_path, audio, sample_rate)

    audio_id = audio_index.add_audio(audio_path)
    audio_index.delete(audio_id)

    # Search should return no results
    results = audio_index.search("test", n_results=1)
    assert len(results) == 0
