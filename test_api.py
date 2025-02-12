import requests


# Base URL
BASE_URL = "http://127.0.0.1:8000"

# Test health check
response = requests.get(f"{BASE_URL}/health")
print("Health Check:", response.json())

# Test ingestion pipeline
ingestion_data = {
    "audio_path": "/path/to/audio/file.mp3",
    "text": "Sample text to ingest",
    "file_path": "/path/to/document.txt",
}
response = requests.post(f"{BASE_URL}/ingest", json=ingestion_data)
print("Ingestion Pipeline:", response.json())

# Test processing pipeline
processing_data = {
    "file_path": "/path/to/audio/file.mp3",
}
response = requests.post(f"{BASE_URL}/process", json=processing_data)
print("Processing Pipeline:", response.json())

# Test query pipeline
query_data = {
    "query": "Find similar audio tracks",
}
response = requests.post(f"{BASE_URL}/query", json=query_data)
print("Query Pipeline:", response.json())
