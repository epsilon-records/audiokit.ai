from fastapi import FastAPI, WebSocket
from .endpoints import router as api_router

app = FastAPI(title="AudioKit-AI Server", version="0.1.0")

# Include API routes under /api/v1
app.include_router(api_router, prefix="/api/v1")

# WebSocket endpoint for real-time audio processing
@app.websocket("/ws/audio")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Dummy processing: echo the received data
            await websocket.send_text(f"Received: {data}")
    except Exception as e:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("audiokit_ai.main:app", host="0.0.0.0", port=8000, reload=True) 