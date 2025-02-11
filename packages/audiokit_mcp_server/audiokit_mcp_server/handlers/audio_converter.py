import asyncio
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import HTTPException
from pydantic import BaseModel

from .audio_presets import (
    AUDIO_PRESETS,
    validate_format_options,
)


class ConversionRequest(BaseModel):
    """Request model for audio conversion"""

    input_file: str
    output_format: str
    preset: Optional[str] = None


class ConversionResponse(BaseModel):
    output_path: str
    duration: float
    format: str
    size: int


class SupportedFormats(BaseModel):
    input_formats: List[str]
    output_formats: List[str]


class BatchConversionRequest(BaseModel):
    """Request model for batch audio conversion"""

    files: List[str]
    output_format: str
    preset: Optional[str] = None


class ConversionProgress(BaseModel):
    """Model for conversion progress"""

    file_name: str
    progress: float
    status: str


class BatchConversionResponse(BaseModel):
    conversions: List[ConversionResponse]
    failed: List[Dict[str, str]]  # path -> error message


SUPPORTED_INPUT_FORMATS = {
    "wav",
    "mp3",
    "aac",
    "ogg",
    "flac",
    "m4a",
    "wma",
    "aiff",
    "alac",
    "opus",
    "webm",
}

SUPPORTED_OUTPUT_FORMATS = {
    "wav",
    "mp3",
    "aac",
    "ogg",
    "flac",
}


async def get_supported_formats() -> SupportedFormats:
    """Get list of supported audio formats"""
    return SupportedFormats(
        input_formats=list(SUPPORTED_INPUT_FORMATS),
        output_formats=list(SUPPORTED_OUTPUT_FORMATS),
    )


async def convert_audio(request: ConversionRequest):
    """Convert a single audio file"""
    try:
        # Conversion logic here
        return {
            "status": "success",
            "output_file": f"{request.input_file}.{request.output_format}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# In-memory storage for conversion progress
conversion_progress: Dict[str, ConversionProgress] = {}


async def monitor_conversion(process: asyncio.subprocess.Process, file_name: str):
    """Monitor ffmpeg conversion progress"""
    while True:
        try:
            if process.stderr is None:
                break

            line = await process.stderr.readline()
            if not line:
                break

            line = line.decode()
            if "time=" in line:
                # Parse ffmpeg progress output
                time_str = line.split("time=")[1].split()[0]
                # Convert time to seconds and calculate progress
                # This is simplified - you'd want more robust parsing
                progress = min(float(time_str.split(":")[0]) * 100, 100)

                conversion_progress[file_name].progress = progress

        except Exception:
            break


async def convert_audio_with_progress(
    input_path: str,
    output_format: str,
    output_path: str | None = None,
    preset: str | None = None,
    options: dict | None = None,
) -> ConversionResponse:
    """Convert audio file with progress monitoring"""
    input_path = Path(input_path)
    file_name = input_path.name

    # Initialize progress tracking
    conversion_progress[file_name] = ConversionProgress(
        file_name=file_name,
        progress=0,
        status="pending",
    )

    try:
        # Apply preset if specified
        if preset and preset in AUDIO_PRESETS:
            options = AUDIO_PRESETS[preset].ffmpeg_options.copy()
            if options:
                options.update(options or {})

        # Validate format-specific options
        if options:
            options = validate_format_options(output_format, options)

        # Previous conversion logic here...
        # (Keep existing conversion code, but update to use asyncio.create_subprocess_exec)

        # Create subprocess with progress monitoring
        process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-i",
            str(input_path),
            *[item for opt in options.items() for item in [f"-{opt[0]}", str(opt[1])]],
            str(output_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Monitor progress
        conversion_progress[file_name].status = "processing"
        monitor_task = asyncio.create_task(monitor_conversion(process, file_name))

        # Wait for conversion to complete
        await process.wait()
        await monitor_task

        if process.returncode != 0:
            raise RuntimeError(f"Conversion failed: {await process.stderr.read()}")

        # Update progress
        conversion_progress[file_name].status = "completed"
        conversion_progress[file_name].progress = 100

        # Return conversion response
        return ConversionResponse(
            output_path=str(output_path),
            duration=get_audio_duration(output_path),
            format=output_format,
            size=output_path.stat().st_size,
        )

    except Exception as e:
        conversion_progress[file_name].status = "failed"
        conversion_progress[file_name].error = str(e)
        raise


async def batch_convert_audio(request: BatchConversionRequest):
    """Convert multiple audio files"""
    try:
        results = []
        for file in request.files:
            single_request = ConversionRequest(
                input_file=file,
                output_format=request.output_format,
                preset=request.preset,
            )
            result = await convert_audio(single_request)
            results.append(result)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_conversion_progress(file_name: str):
    """Get progress of a specific conversion"""
    if file_name not in conversion_progress:
        raise HTTPException(status_code=404, detail="Conversion not found")
    return conversion_progress[file_name]
