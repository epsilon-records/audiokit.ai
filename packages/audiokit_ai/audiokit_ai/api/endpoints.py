# CONFIDENTIAL AND PROPRIETARY
#
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
#
# This software is confidential and proprietary.
#

#
# This file is part of the AudioKit AI package.
#


import asyncio
import base64
import time
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel

from audiokit_ai.core.logger import logger
from audiokit_ai.core.security import verify_token
from audiokit_ai.services import processing
from audiokit_ai.services.exceptions import (
    InvalidAudioFormatError,
    ProcessingError,
    ResourceError,
)


router = APIRouter()


# Progress tracking state
class ProgressTracker:
    def __init__(self):
        self.tasks: Dict[str, int] = {}
        self.subscriptions: Dict[str, str] = {}  # sid -> task_id

    async def update_progress(self, task_id: str, progress: int):
        """Update progress for a task and notify subscribers"""
        self.tasks[task_id] = progress
        await sio.emit(
            "progress",
            {
                "task_id": task_id,
                "progress": progress,
            },
            room=task_id,
        )


progress_tracker = ProgressTracker()


@sio.on("connect")
async def handle_connect(sid, environ):
    logger.debug(f"Client connected: {sid}")
    await sio.save_session(sid, {"last_ping": time.time()})
    await sio.emit("heartbeat", {"ts": time.time()}, to=sid)


@sio.on("disconnect")
async def handle_disconnect(sid):
    logger.debug(f"Client disconnected: {sid}")
    if sid in progress_tracker.subscriptions:
        del progress_tracker.subscriptions[sid]


@sio.on("subscribe")
async def handle_subscribe(sid, data):
    """Handle client subscription to progress updates"""
    try:
        task_id = data["task_id"]
        progress_tracker.subscriptions[sid] = task_id
        await sio.save_session(sid, {"task_id": task_id})
        await sio.enter_room(sid, task_id)

        # Send current progress if available
        if task_id in progress_tracker.tasks:
            await sio.emit(
                "progress",
                {
                    "task_id": task_id,
                    "progress": progress_tracker.tasks[task_id],
                },
                to=sid,
            )

    except Exception as e:
        logger.error(f"Subscription error: {e!s}")
        await sio.emit("error", {"message": str(e)}, to=sid)


async def broadcast_progress(task_id: str, progress: int):
    """Update progress for all subscribed clients"""
    try:
        await sio.emit(
            "progress",
            {"task_id": task_id, "progress": progress},
            room=task_id,
        )
    except Exception as e:
        logger.warning(f"Progress broadcast failed: {e!s}")


# Common processing handler
async def handle_processing(
    endpoint: str,
    file: UploadFile,
    processor: callable,
    task_id: str = None,
):
    """Generic handler for audio processing endpoints"""
    try:
        task_id = task_id or str(uuid4())
        progress_tracker.tasks[task_id] = 0

        # Start processing in background
        result = await processor(
            file,
            progress_callback=lambda p: asyncio.create_task(
                broadcast_progress(task_id, p),
            ),
        )

        # Read and encode processed file
        with open(result["file_path"], "rb") as f:
            audio_data = base64.b64encode(f.read()).decode("utf-8")

        # Cleanup
        del progress_tracker.tasks[task_id]
        return {"task_id": task_id, "result": audio_data}

    except Exception as e:
        logger.error(f"Processing failed: {e!s}")
        await broadcast_progress(task_id, -1)  # Error state
        raise HTTPException(status_code=500, detail=str(e))


# Audio processing endpoints
@router.post("/denoise_speech")
async def denoise_speech(
    file: UploadFile = File(...),
    task_id: str = Form(None),
):
    """Reduce noise in speech/vocal audio using DeepFilterNet"""
    return await handle_processing(
        "denoise_speech",
        file,
        processing.denoise_speech,
        task_id,
    )


@router.post("/denoise_music")
async def denoise_music(
    file: UploadFile = File(...),
    task_id: str = Form(None),
):
    """Intelligently denoise music by separating and recombining stems"""
    return await handle_processing(
        "denoise_music",
        file,
        processing.denoise_music,
        task_id,
    )


# Additional endpoints using the generic handler
@router.post("/separate_stems")
async def separate_stems(file: UploadFile = File(...)):
    return await handle_processing("separate_stems", file, processing.separate_stems)


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    return await handle_processing("transcribe", file, processing.transcribe)


@router.post("/auto_master")
async def auto_master_audio(file: UploadFile = File(...)):
    return await handle_processing("auto_master", file, processing.auto_master)


@router.post("/clone_voice")
async def clone_voice(file: UploadFile = File(...)):
    return await handle_processing("clone_voice", file, processing.clone_voice)


@router.post("/midi_to_audio")
async def midi_to_audio(file: UploadFile = File(...)):
    return await handle_processing("midi_to_audio", file, processing.midi_to_audio)


@router.post("/generate_music")
async def generate_music(file: UploadFile = File(...)):
    return await handle_processing("generate_music", file, processing.generate_music)


class AudioRequest(BaseModel):
    audio_file: str  # Path or URL to the audio file
    options: Dict[str, Any] = {}


def verify_api_key(request: Request, api_key: str = Depends(verify_token)):
    """Enhanced API key verification combining JWT and Redis"""
    redis_client = request.app.state.redis_client
    if not redis_client.exists(f"api_key:{api_key}"):
        logger.warning(f"Invalid API key attempt: {api_key}")
        raise HTTPException(status_code=401, detail="Unauthorized")
    return api_key


@router.post("/search_by_sound")
async def search_by_sound(
    request: Request,
    audio_request: AudioRequest,
    api_key: str = Depends(verify_api_key),
):
    """Vector-based audio similarity search"""
    try:
        response = (
            request.app.state.weaviate_client.query.get(
                "Audio",
                ["metadata", "audio_file"],
            )
            .with_near_audio(audio_request.audio_file)
            .with_limit(5)
            .do()
        )
        return {
            "status": "success",
            "results": response.get("data", {}).get("Get", {}).get("Audio", []),
        }
    except Exception as e:
        logger.error(f"Weaviate search error: {e!s}")
        raise HTTPException(status_code=500, detail="Search operation failed")


@router.post("/identify_song")
async def identify_song(
    request: Request,
    audio_request: AudioRequest,
    api_key: str = Depends(verify_api_key),
):
    """Song identification through audio fingerprinting"""
    try:
        response = (
            request.app.state.weaviate_client.query.get(
                "Songs",
                ["title", "artist", "audio_file"],
            )
            .with_near_audio(audio_request.audio_file)
            .with_limit(1)
            .do()
        )
        results = response.get("data", {}).get("Get", {}).get("Songs", [])
        return {
            "status": "success",
            "match_found": len(results) > 0,
            "results": results[0] if results else {},
        }
    except Exception as e:
        logger.error(f"Song identification error: {e!s}")
        raise HTTPException(status_code=500, detail="Identification failed")


@router.post("/detect_genre", dependencies=[Depends(verify_token)])
async def detect_genre(file: UploadFile = File(...)):
    try:
        result = processing.detect_genre(file)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/denoise")
async def denoise_endpoint(file: UploadFile = File(...)):
    try:
        return await denoise_music(file)
    except InvalidAudioFormatError as e:
        raise HTTPException(400, detail=str(e))
    except ResourceError as e:
        raise HTTPException(503, detail=str(e))
    except ProcessingError as e:
        raise HTTPException(500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e!s}")
        raise HTTPException(500, detail="Internal server error")
