"""Banana.dev client integration"""
import os
from typing import Optional

try:
    from banana_dev import Client
except ImportError:
    # Fallback implementation when banana_dev is not available
    class Client:
        def __init__(self, api_key: Optional[str] = None, url: Optional[str] = None, **kwargs):
            self.api_key = api_key
            self.url = url
        
        async def run(self, *args, **kwargs):
            return {"message": "Banana client not available"}

# Initialize with environment variables or defaults
banana = Client(
    api_key=os.getenv("BANANA_API_KEY", "dummy_key"),
    url=os.getenv("BANANA_API_URL", "wss://audio.banana.dev")
)

class BananaClient:
    def __init__(self):
        self.client = Client(
            api_key=os.getenv("BANANA_API_KEY", "dummy_key"),
            url=os.getenv("BANANA_API_URL", "wss://audio.banana.dev")
        )
    
    async def process_audio(self, audio: bytes, params: dict) -> bytes:
        """Process audio with Banana.dev"""
        response = await self.client.run(
            input=audio,
            params=params
        )
        return response["processed"]

    async def transcribe(self, audio: bytes) -> str:
        """Transcribe audio using Whisper"""
        response = await self.client.run(
            input=audio,
            params={"task": "transcribe"}
        )
        return response["text"] 