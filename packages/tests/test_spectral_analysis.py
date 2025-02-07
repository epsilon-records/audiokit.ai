import pytest
import requests

def test_spectral_analysis():
    test_file = "tests/data/sample.wav"
    
    with open(test_file, "rb") as f:
        response = requests.post(
            "http://localhost:8000/api/v1/analyze/spectral",
            files={"audio_file": f},
            params={"features": ["mfcc", "centroid"]}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "analysis" in data
    assert "mfcc" in data["analysis"]
    assert "centroid" in data["analysis"]
    assert isinstance(data["duration"], float)
    assert data["sample_rate"] > 0 