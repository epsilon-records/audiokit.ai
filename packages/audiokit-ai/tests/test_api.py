"""Tests for AudioKit AI API endpoints."""
import pytest
from fastapi.testclient import TestClient
from audiokit_ai.main import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

@pytest.fixture
def test_audio():
    """Create test audio data."""
    import numpy as np
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
    return audio.tobytes()

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_analyze_endpoint(client, test_audio):
    """Test audio analysis endpoint."""
    response = client.post(
        "/analyze",
        files={"file": ("test.wav", test_audio)},
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "duration" in data
    assert "sample_rate" in data
    assert "peak_amplitude" in data

def test_analyze_invalid_audio(client):
    """Test analysis with invalid audio data."""
    response = client.post(
        "/analyze",
        files={"file": ("test.wav", b"invalid audio data")},
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 400

def test_missing_api_key(client, test_audio):
    """Test request without API key."""
    response = client.post(
        "/analyze",
        files={"file": ("test.wav", test_audio)}
    )
    assert response.status_code == 401

def test_analyze_invalid_file_type(client):
    response = client.post(
        "/analyze",
        files={"file": ("test.txt", b"invalid content")},
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 400
    assert "Unsupported MIME type" in response.json()["detail"]

def test_analyze_large_file(client):
    large_file = b"a" * (50 * 1024 * 1024 + 1)  # 50MB + 1 byte
    response = client.post(
        "/analyze",
        files={"file": ("test.wav", large_file)},
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 413 