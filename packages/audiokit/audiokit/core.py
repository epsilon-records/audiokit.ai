"""Main AudioKit AI pipeline"""

import asyncio

from .logger import Logger
from .db import get_artist_data_from_db
from .models import ArtistData
from .processor import DocumentProcessor
from .generator import EPKGenerator, InternalReportGenerator, BookingEmailGenerator
from config import cfg


async def run_audiokit_ai_pipeline(artist_id: str) -> None:
    """Run the AudioKit AI pipeline for a given artist"""
    pipeline_start = Logger.start_task("Starting full marketing pipeline")

    try:
        Logger.info(f"Starting pipeline for artist ID: {artist_id}")

        # Fetch artist data
        Logger.info("Fetching artist data from database")
        fetch_start = Logger.start_task("Fetching artist data")
        artist_data_raw = get_artist_data_from_db(artist_id)
        artist_data = ArtistData(**artist_data_raw)
        Logger.end_task(fetch_start, "Artist data fetched successfully")
        Logger.info(f"Artist data retrieved for: {artist_data.stage_name}")

        # Initialize processor
        processor = DocumentProcessor(artist_id)

        # Process artist data
        Logger.info("Processing artist data")
        process_start = Logger.start_task("Data processing")

        # Core artist data
        await processor.process_artist_data(artist_data)

        # TODO: Add processing for:
        # - Social media data
        # - Press coverage
        # - Analytics
        # - Performance history

        Logger.end_task(process_start, "Data processing completed")

        # Generate content
        Logger.info("Starting content generation")
        generate_start = Logger.start_task("Content generation")

        # Generate EPK
        epk_generator = EPKGenerator(artist_id=artist_id, model_name=cfg.models.epk)
        epk_content = await epk_generator.generate_epk()
        await processor.process_generated_content("epk", epk_content)

        # Generate internal report
        report_generator = InternalReportGenerator(
            artist_id=artist_id, model_name=cfg.models.internal_report
        )
        report_content = await report_generator.generate_report()
        await processor.process_generated_content("internal_report", report_content)

        # Generate booking email
        email_generator = BookingEmailGenerator(
            artist_id=artist_id, model_name=cfg.models.booking
        )
        email_content = await email_generator.generate_email()
        await processor.process_generated_content("booking_email", email_content)

        Logger.end_task(generate_start, "Content generation completed")

        Logger.end_task(pipeline_start, "Full marketing pipeline completed")
        Logger.success(f"✅ All tasks completed for {artist_data.stage_name}")

    except Exception as e:
        Logger.error(f"Error in marketing pipeline: {str(e)}")
        raise


if __name__ == "__main__":
    artist_id = "fdf3afd2-a3d8-462c-b2dc-7e0805573d03"
    asyncio.run(run_audiokit_ai_pipeline(artist_id))
