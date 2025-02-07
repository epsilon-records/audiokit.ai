from fastapi import APIRouter, BackgroundTasks, status
from audiokit_core.models.schemas import (
    AudioProcessingRequest,
    ProcessedAudioResponse,
    ErrorResponse
)
from audiokit_core.exceptions import ProcessingError
from ..services.processing import AudioProcessor
from ..storage.jobs import JobStore

router = APIRouter()
processor = AudioProcessor()
job_store = JobStore()

@router.post(
    "/process",
    response_model=ProcessedAudioResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Processing error"}
    }
)
async def process_audio(
    request: AudioProcessingRequest,
    background_tasks: BackgroundTasks
):
    try:
        job = job_store.create_job()
        background_tasks.add_task(processor.process, job.id, request)
        
        return ProcessedAudioResponse(
            job_id=job.id,
            status=job.status,
            created_at=job.created_at
        )
    except ValueError as e:
        raise ProcessingError(f"Invalid input: {str(e)}")
    except Exception as e:
        raise ProcessingError(f"Processing failed: {str(e)}")

@router.get("/results/{job_id}", response_model=ProcessedAudioResponse)
async def get_results(job_id: str):
    job = job_store.get_job(job_id)
    if not job:
        raise ProcessingError("Job not found", status_code=404)
    
    return job.to_response()

# Defines FastAPI endpoints
# Handles HTTP requests/responses
# Manages background tasks and job status 