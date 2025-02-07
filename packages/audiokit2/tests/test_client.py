import pytest
from audiokit.client import AudioKitClient
import httpx
from httpx import Response

# A dummy transport to simulate HTTP responses in tests
class DummyTransport(httpx.BaseTransport):
    def handle_request(self, request):
        return Response(200, json={"status": "success", "result": "dummy"})

@pytest.fixture
def client(monkeypatch):
    # Override httpx.post for testing using a dummy transport
    original_post = httpx.post
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: Response(200, json={"status": "success", "result": "dummy"}))
    sdk_client = AudioKitClient(base_url="http://dummy", jwt_token="dummytoken")
    yield sdk_client
    monkeypatch.setattr(httpx, "post", original_post)

def test_denoise(client):
    result = client.denoise("dummy.wav")
    assert result["result"] == "dummy" 