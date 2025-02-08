# CONFIDENTIAL AND PROPRIETARY
# 
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
# 
# This software is confidential and proprietary.
# 

# 
# This file is part of the AudioKit AI package.
# 

import pytest
from fastapi.testclient import TestClient
from audiokit_ai.main import app, verify_token
import subprocess
import time
import httpx
from unittest.mock import MagicMock
from audiokit_ai.core.logger import logger

# Override the token dependency for testing purposes
app.dependency_overrides[verify_token] = lambda: {}

client = TestClient(app)

@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)

@pytest.fixture(scope="module")
def live_server():
    # Start the server in a separate process
    process = subprocess.Popen(
        ["uvicorn", "audiokit_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
    )
    
    # Wait for server to start
    time.sleep(2)
    
    yield process
    
    # Clean up
    process.terminate()
    process.wait()

def test_denoise_endpoint(test_client):
    """Test the denoise endpoint"""
    response = test_client.post(
        "/api/denoise",
        files={"file": ("test.wav", b"dummy data", "audio/wav")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data

def test_server_start(test_client):
    """Test that the server starts and responds to health check"""
    response = test_client.get("/")
    assert response.status_code == 404  # No root endpoint, should return 404

def test_live_server(live_server):
    """Test that the live server is running and responding"""
    try:
        response = httpx.get("http://localhost:8000/")
        assert response.status_code == 404  # No root endpoint, should return 404
    except httpx.ConnectError:
        pytest.fail("Server failed to start")

@pytest.fixture
def mock_speech_client():
    client = MagicMock()
    client.recognize.return_value = MagicMock(transcript="test transcription")
    return client 

def test_denoise_audio(test_client):
    with open("tests/test_audio.wav", "rb") as f:
        response = test_client.post("/api/denoise", files={"file": f})
        logger.info(f"Test response: {response.status_code}")
        assert response.status_code == 200 