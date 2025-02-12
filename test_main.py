from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingestion_pipeline():
    response = client.post(
        "/ingest",
        json={
            "audio_path": "/path/to/audio/file.mp3",
            "text": "Sample text",
            "file_path": "/path/to/document.txt",
        },
    )
    assert response.status_code == 200
    assert "audio" in response.json()
    assert "text" in response.json()
    assert "file" in response.json()


def test_ingestion_pipeline_audio_only():
    response = client.post(
        "/ingest",
        json={"audio_path": "/path/to/audio/file.mp3"},
    )
    assert response.status_code == 200
    assert "audio" in response.json()
    assert "text" not in response.json()
    assert "file" not in response.json()


def test_ingestion_pipeline_text_only():
    response = client.post(
        "/ingest",
        json={"text": "Sample text"},
    )
    assert response.status_code == 200
    assert "text" in response.json()
    assert "audio" not in response.json()
    assert "file" not in response.json()


def test_ingestion_pipeline_file_only():
    response = client.post(
        "/ingest",
        json={"file_path": "/path/to/document.txt"},
    )
    assert response.status_code == 200
    assert "file" in response.json()
    assert "audio" not in response.json()
    assert "text" not in response.json()


def test_processing_pipeline():
    response = client.post(
        "/process",
        json={"file_path": "/path/to/audio/file.mp3"},
    )
    assert response.status_code == 200
    assert "processed" in response.json()
    assert "metadata" in response.json()


def test_query_pipeline():
    response = client.post(
        "/query",
        json={"query": "Find similar audio tracks"},
    )
    assert response.status_code == 200
    assert "query_result" in response.json()
    assert "search_result" in response.json()
