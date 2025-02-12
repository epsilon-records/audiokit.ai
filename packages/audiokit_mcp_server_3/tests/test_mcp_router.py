from audiokit_mcp_server.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_process_query():
    response = client.post("/mcp/process", json={"query": "test"})
    data = response.json()
    # Verify that the response is structured correctly.
    assert response.status_code == 200
    assert data["status"] == "success"
    assert "response" in data
    resp = data["response"]
    assert isinstance(resp, dict)
    assert "answer" in resp
    assert "sources" in resp
    assert isinstance(resp["sources"], list)
