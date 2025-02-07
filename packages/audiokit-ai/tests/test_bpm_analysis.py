import requests

def test_bpm_analysis():
    test_file = "tests/data/drum_loop.wav"
    
    with open(test_file, "rb") as f:
        response = requests.post(
            "http://localhost:8000/api/v1/analyze/bpm",
            files={"audio_file": f}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert 120 <= data["bpm"] <= 180  # Expected range for test file
    assert data["method"] == "librosa" 