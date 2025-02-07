# New file for cover art generation endpoint
from fastapi import APIRouter, File, UploadFile
from audiokit_core.image_generation import AudioVisualizer

router = APIRouter()
visualizer = AudioVisualizer()

@router.post("/api/v1/cover-art")
async def generate_cover_art(
    audio_file: UploadFile = File(...),
    style: str = "modern",
    resolution: str = "1024x1024"
):
    """Generate cover artwork from audio analysis"""
    audio_data = await audio_file.read()
    
    # Analyze audio features
    analysis = visualizer.analyze_audio(audio_data)
    
    # Generate cover art
    image_bytes = visualizer.generate_artwork(
        audio_features=analysis,
        style=style,
        resolution=resolution
    )
    
    return Response(content=image_bytes, media_type="image/png") 