def test_denoise(client):
    response = client.post(
        "/api/v1/denoise", 
        files={"audio": ("test.wav", b"dummy data", "audio/wav")}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Denoise complete"

def test_websocket(client):
    with client.websocket_connect("/ws/audio") as websocket:
        websocket.send_text("Hello")
        data = websocket.receive_text()
        assert "Received: Hello" in data 