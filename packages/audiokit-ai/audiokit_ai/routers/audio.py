from fastapi import APIRouter, UploadFile, Depends
from audiokit_core.models.schemas import AudioAnalysis
from ..auth import AuthHandler

router = APIRouter()

@router.post(
    "/analyze",
    response_model=AudioAnalysis,
    tags=["Audio"],
    summary="Analyze audio file",
    responses={
        200: {"description": "Successful analysis"},
        400: {"description": "Invalid input or processing error"},
        401: {"description": "Missing or invalid authentication"},
        413: {"description": "File too large"},
        429: {"description": "Rate limit exceeded"}
    }
)
async def analyze_audio(
    file: UploadFile,
    auth_handler: AuthHandler = Depends(AuthHandler.api_key_auth)
) -> AudioAnalysis:
    """Analyze audio file with AI processing"""
    # Existing analysis implementation... 