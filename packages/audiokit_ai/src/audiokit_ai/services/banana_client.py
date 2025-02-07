"""Banana.dev client integration"""
import os
from banana_dev import Client

class BananaClient:
    def __init__(self):
        self.client = Client(
            api_key=os.getenv("BANANA_API_KEY"),
            model_key="audiokit-v1",
            url="wss://audio.banana.dev",
            protocol="ws"
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