# CONFIDENTIAL AND PROPRIETARY
#
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
#
# This software is confidential and proprietary.
#

#
# This file is part of the AudioKit AI package.
#

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, WebSocket

try:
    from fastapi_limiter.depends import WebSocketRateLimiter
except ImportError:
    # Fallback for when rate limiting is not available
    class WebSocketRateLimiter:
        def __init__(self, *args, **kwargs):
            pass

        async def __call__(self, websocket):
            return True


from audiokit_ai.services import processing
from audiokit_ai.core.security import verify_token

router = APIRouter(prefix="/api/v1")


# Audio processing endpoints (all protected via JWT dependency)
@router.post("/denoise", dependencies=[Depends(verify_token)])
async def denoise_audio(file: UploadFile = File(...)):
    try:
        result = await processing.denoise(file)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/separate", dependencies=[Depends(verify_token)])
async def separate_audio(file: UploadFile = File(...)):
    try:
        result = await processing.separate_audio(file)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto_master", dependencies=[Depends(verify_token)])
async def auto_master_audio(file: UploadFile = File(...)):
    try:
        result = processing.auto_master(file)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe", dependencies=[Depends(verify_token)])
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        result = await processing.transcribe(file)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clone_voice", dependencies=[Depends(verify_token)])
async def clone_voice(file: UploadFile = File(...)):
    try:
        result = processing.clone_voice(file)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/midi_to_audio", dependencies=[Depends(verify_token)])
async def midi_to_audio(file: UploadFile = File(...)):
    try:
        result = processing.midi_to_audio(file)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate_music", dependencies=[Depends(verify_token)])
async def generate_music(file: UploadFile = File(...)):
    try:
        result = processing.generate_music(file)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search_by_sound", dependencies=[Depends(verify_token)])
async def search_by_sound(file: UploadFile = File(...)):
    try:
        result = processing.search_by_sound(file)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/identify_song", dependencies=[Depends(verify_token)])
async def identify_song(file: UploadFile = File(...)):
    try:
        result = processing.identify_song(file)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect_genre", dependencies=[Depends(verify_token)])
async def detect_genre(file: UploadFile = File(...)):
    try:
        result = processing.detect_genre(file)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Real-time audio streaming via WebSocket
@router.websocket("/ws/stream")
async def audio_stream(websocket: WebSocket):
    await websocket.accept()
    rate_limiter = WebSocketRateLimiter(times=100, seconds=60)
    try:
        while True:
            await rate_limiter(websocket)
            audio_chunk = await websocket.receive_bytes()
            processed = await processing.denoise(audio_chunk)
            await websocket.send_bytes(processed)
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
