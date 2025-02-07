import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import verify_token

# Override the token dependency for testing purposes
app.dependency_overrides[verify_token] = lambda: {}

client = TestClient(app)

def test_denoise_endpoint():
    response = client.post(
        "/api/denoise",
        files={"file": ("test.wav", b"dummy data", "audio/wav")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data 