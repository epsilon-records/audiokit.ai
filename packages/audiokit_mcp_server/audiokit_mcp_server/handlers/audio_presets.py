from typing import Dict

from pydantic import BaseModel, Field


class AudioPreset(BaseModel):
    name: str
    description: str
    ffmpeg_options: Dict[str, str]


class FormatOptions(BaseModel):
    """Validation rules for format-specific options"""

    bitrate: str = Field(pattern=r"^\d+k$", description="Bitrate (e.g., '192k')")
    sample_rate: int = Field(ge=8000, le=192000, description="Sample rate in Hz")
    channels: int = Field(ge=1, le=8, description="Number of audio channels")


AUDIO_PRESETS = {
    "voice": AudioPreset(
        name="voice",
        description="Optimized for voice recordings",
        ffmpeg_options={
            "b:a": "64k",
            "ar": "22050",
            "ac": "1",
            "compression_level": "8",
        },
    ),
    "music_high": AudioPreset(
        name="music_high",
        description="High quality music",
        ffmpeg_options={
            "b:a": "320k",
            "ar": "48000",
            "ac": "2",
            "compression_level": "0",
        },
    ),
    "music_medium": AudioPreset(
        name="music_medium",
        description="Balanced quality/size for music",
        ffmpeg_options={
            "b:a": "192k",
            "ar": "44100",
            "ac": "2",
            "compression_level": "3",
        },
    ),
    "podcast": AudioPreset(
        name="podcast",
        description="Optimized for podcasts",
        ffmpeg_options={
            "b:a": "96k",
            "ar": "44100",
            "ac": "1",
            "compression_level": "5",
        },
    ),
}

# Format-specific validation rules
FORMAT_CONSTRAINTS = {
    "mp3": {
        "valid_bitrates": {"64k", "96k", "128k", "192k", "256k", "320k"},
        "valid_sample_rates": {8000, 11025, 22050, 44100, 48000},
        "max_channels": 2,
    },
    "aac": {
        "valid_bitrates": {"64k", "96k", "128k", "192k", "256k"},
        "valid_sample_rates": {8000, 11025, 22050, 44100, 48000},
        "max_channels": 8,
    },
    "flac": {
        "valid_sample_rates": {8000, 11025, 22050, 44100, 48000, 96000, 192000},
        "max_channels": 8,
        "compression_levels": set(range(13)),
    },
}


def validate_format_options(format: str, options: dict) -> dict:
    """Validate and normalize format-specific options"""
    if format not in FORMAT_CONSTRAINTS:
        return options

    constraints = FORMAT_CONSTRAINTS[format]

    if "b:a" in options and "valid_bitrates" in constraints:
        if options["b:a"] not in constraints["valid_bitrates"]:
            raise ValueError(
                f"Invalid bitrate for {format}: {options['b:a']}. "
                f"Valid values: {constraints['valid_bitrates']}",
            )

    if "ar" in options and "valid_sample_rates" in constraints:
        sr = int(options["ar"])
        if sr not in constraints["valid_sample_rates"]:
            raise ValueError(
                f"Invalid sample rate for {format}: {sr}. "
                f"Valid values: {constraints['valid_sample_rates']}",
            )

    if "ac" in options and "max_channels" in constraints:
        channels = int(options["ac"])
        if channels > constraints["max_channels"]:
            raise ValueError(
                f"Too many channels for {format}: {channels}. "
                f"Maximum: {constraints['max_channels']}",
            )

    if "compression_level" in options and "compression_levels" in constraints:
        level = int(options["compression_level"])
        if level not in constraints["compression_levels"]:
            raise ValueError(
                f"Invalid compression level for {format}: {level}. "
                f"Valid values: {constraints['compression_levels']}",
            )

    return options
