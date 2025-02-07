def test_key_detection():
    test_file = "tests/data/c_major_scale.wav"
    
    with open(test_file, "rb") as f:
        response = requests.post(
            "http://localhost:8000/api/v1/analyze/key",
            files={"audio_file": f}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["key"] in ["C major", "A minor"]  # Relative major/minor
    assert 0.5 <= data["confidence"] <= 1.0 