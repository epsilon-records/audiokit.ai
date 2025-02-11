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
import json
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, WebSocket
from fastapi.websockets import WebSocketDisconnect

from audiokit_ai.core.logger import logger


try:
    from fastapi_limiter.depends import WebSocketRateLimiter
except ImportError:
    # Fallback for when rate limiting is not available
    class WebSocketRateLimiter:
        def __init__(self, *args, **kwargs):
            pass

        async def __call__(self, websocket):
            return True


from audiokit_ai.core.security import verify_token
from audiokit_ai.services import processing


router = APIRouter()


# Audio processing endpoints (all protected via JWT dependency)
# @router.post("/denoise", dependencies=[Depends(verify_token)])
@router.post("/denoise_speech", response_model=dict)
async def denoise_speech(
    file: UploadFile = File(...),
    task_id: str = Form(None),  # Accept task_id from form data
):
    """Reduce noise in speech/vocal audio using DeepFilterNet"""
    # Use the provided task_id or generate a new one if needed.
    if not task_id:
        task_id = str(uuid4())
    progress_tracker.tasks[task_id] = 0

    try:
        # Start processing in background
        result = await processing.denoise_speech(
            file,
            # Callback sends progress updates using the same task_id
            progress_callback=lambda p: asyncio.create_task(
                progress_tracker.broadcast_progress(task_id, p),
            ),
        )

        # Read the processed file and encode it
        with open(result["file_path"], "rb") as f:
            audio_data = base64.b64encode(f.read()).decode("utf-8")

        # Clean up
        del progress_tracker.tasks[task_id]
        return {"task_id": task_id, "result": audio_data}
    except Exception as e:
        logger.error(f"Speech denoising failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/denoise_music", response_model=dict)
async def denoise_music(
    file: UploadFile = File(...),
    task_id: str = Form(None),  # Accept task_id from form data
):
    """Intelligently denoise music by separating, denoising specific stems, and recombining"""
    if not task_id:
        task_id = str(uuid4())
    progress_tracker.tasks[task_id] = 0

    try:
        # Start processing in background
        result = await processing.denoise_music(
            file,
            progress_callback=lambda p: asyncio.create_task(
                progress_tracker.broadcast_progress(task_id, p),
            ),
        )

        # Read the processed file and encode it
        with open(result["file_path"], "rb") as f:
            audio_data = base64.b64encode(f.read()).decode("utf-8")

        # Clean up
        del progress_tracker.tasks[task_id]
        return {"task_id": task_id, "result": audio_data}
    except Exception as e:
        logger.error(f"Music denoising failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/separate_stems", dependencies=[Depends(verify_token)])
async def separate_stems(file: UploadFile = File(...)):
    try:
        result = await processing.separate_stems(file)
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


# Replace the existing ProgressTracker definition with the following:


class ProgressTracker:
    def __init__(self):
        self.tasks = {}
        # Use a dict mapping each websocket to its message queue.
        self.connections = {}
        # Use a dict mapping each websocket to its subscribed task ID
        self.subscriptions = {}
        # Use a flag to track if the Redis listener has started
        self._redis_listener_started = False
        # Initialize Redis client for multi-worker progress updates
        import redis.asyncio as redis

        from audiokit_ai.core.config import settings  # Ensure settings are imported

        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            decode_responses=True,
        )

    async def add_connection(self, websocket: WebSocket):
        # Accept the WebSocket and create a dedicated queue.
        await websocket.accept()
        queue = asyncio.Queue()
        self.connections[websocket] = queue
        # Launch a sender task for this connection.
        asyncio.create_task(self.sender(websocket, queue))
        logger.debug("Added new connection")
        # Start the Redis listener if not already running
        if not self._redis_listener_started:
            self._redis_listener_started = True
            asyncio.create_task(self.start_redis_listener())

    async def sender(self, websocket: WebSocket, queue: asyncio.Queue):
        # This loop continuously sends messages from the queue to the client.
        try:
            while True:
                message = await queue.get()
                await websocket.send_json(message)
                logger.debug("Sent progress update to connection")
        except Exception as e:
            logger.error(f"Error in sender task: {e}")
            self.remove_connection(websocket)

    def remove_connection(self, websocket: WebSocket):
        if websocket in self.connections:
            del self.connections[websocket]
            if websocket in self.subscriptions:
                del self.subscriptions[websocket]
            logger.debug("Removed connection")

    async def broadcast_progress(self, task_id: str, progress: int):
        # Ensure progress stays within bounds
        progress = min(max(progress, 0), 100)
        logger.debug(
            f"Broadcasting progress update via local connections: {progress}% for task {task_id}",
        )
        logger.debug(f"Active local connections: {len(self.connections)}")
        message = {
            "type": "progress",
            "task_id": task_id,
            "progress": progress,
        }
        # Update stored progress
        self.tasks[task_id] = progress
        # Put the message on each connection's local queue.
        for websocket, queue in list(self.connections.items()):
            try:
                await queue.put(message)
            except Exception as e:
                logger.error(f"Error queuing message for local connection: {e}")
                self.remove_connection(websocket)

        # Also publish the progress update to Redis (for multi-worker communication)
        try:
            json_message = json.dumps(message)
            logger.debug(
                f"Publishing progress update to Redis channel 'progress_updates': {json_message}",
            )
            publish_result = await self.redis_client.publish(
                "progress_updates",
                json_message,
            )
            logger.debug(
                f"Published progress update to Redis channel 'progress_updates', publish result: {publish_result}",
            )
        except Exception as e:
            logger.error(f"Error publishing progress update to Redis: {e}")

    async def start_redis_listener(self):
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe("progress_updates")
        logger.debug("Started Redis listener for progress updates")
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1.0,
            )
            if message:
                logger.debug(f"Received raw message from Redis: {message}")
                try:
                    raw_data = message["data"]
                    logger.debug(f"Raw data from Redis message: {raw_data}")
                    try:
                        data = json.loads(raw_data)
                        logger.debug(f"Decoded Redis message: {data}")
                    except Exception as json_err:
                        logger.error(
                            f"Failed to decode Redis message: {raw_data}. Error: {json_err}",
                        )
                        continue
                    task = data.get("task_id")
                    logger.debug(f"Redis message task id: {task}")
                    # For each websocket subscribed locally, push the message if task id matches
                    for ws, sub_task in list(self.subscriptions.items()):
                        logger.debug(
                            f"WebSocket {ws} is subscribed for task: {sub_task}",
                        )
                        if sub_task == task:
                            queue = self.connections.get(ws)
                            if queue:
                                await queue.put(data)
                                logger.debug(
                                    f"Queued Redis message to websocket {ws} for task {task}.",
                                )
                            else:
                                logger.debug(f"No queue found for websocket {ws}.")
                except Exception as e:
                    logger.error(f"Error processing Redis message: {e}")
            await asyncio.sleep(0.01)


progress_tracker = ProgressTracker()


# Update the WebSocket endpoint to only handle the subscription message,
# then simply to keep the connection open.
@router.websocket("/ws/progress", name="websocket_progress")
async def websocket_progress(websocket: WebSocket):
    logger.debug("New WebSocket connection request")
    try:
        # Register connection
        await progress_tracker.add_connection(websocket)
        logger.debug("WebSocket connection accepted")

        # Wait for the initial subscription message.
        logger.debug("Waiting for subscription message")
        data = await websocket.receive_json()
        logger.debug(f"Received subscription message: {data}")
        if data.get("type") == "subscribe":
            task_id = data["task_id"]
            logger.debug(f"Client subscribed to task: {task_id}")
            # Record the subscription for this websocket.
            progress_tracker.subscriptions[websocket] = task_id
            # Send initial progress if available.
            if task_id in progress_tracker.tasks:
                initial_progress = progress_tracker.tasks[task_id]
                logger.debug(f"Sending initial progress: {initial_progress}%")
                await progress_tracker.connections[websocket].put(
                    {
                        "type": "progress",
                        "task_id": task_id,
                        "progress": initial_progress,
                    },
                )
        # Keep the connection alive.
        while True:
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        logger.debug("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        progress_tracker.remove_connection(websocket)
