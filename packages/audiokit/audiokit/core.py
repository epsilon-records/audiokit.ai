import os
from .logger import Logger
from .db import get_artist_data_from_db
from .llm import (
    generate_reports,
    integrate_reports,
    beautify_report,
    generate_booking_emails,
)
from .utils import save_emails_to_file
from config import cfg
from .models import ArtistData


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

        # Generate reports
        Logger.info("Starting report generation process")
        report_start = Logger.start_task("Report generation")
        all_reports = await generate_reports(artist_data_raw)
        Logger.end_task(report_start, "Report generation completed")
        Logger.success(
            f"Generated {len(all_reports.epk)} EPKs and {len(all_reports.internal)} internal reports"
        )

        # Integrate reports
        integrated_reports = await integrate_reports(all_reports, artist_data.name_slug)

        # Beautify reports
        Logger.info("Starting report beautification process")
        beautify_start = Logger.start_task("Report beautification")

        for report_type, content in integrated_reports.items():
            if content:
                beautified = await beautify_report(
                    content, report_type, artist_data.name_slug
                )
                integrated_reports[report_type] = beautified

        Logger.end_task(beautify_start, "Report beautification completed")
        Logger.success("Reports beautified successfully")

        # Save reports
        Logger.info("Starting report saving process")
        save_start = Logger.start_task("Saving reports")
        cache_dir = cfg.get_path("cache_dir", artist_data.name_slug)

        # Save beautified reports to cache
        Logger.info("Saving beautified reports to cache")
        os.makedirs(cache_dir, exist_ok=True)

        for report_type, content in integrated_reports.items():
            if content:
                filename = cache_dir.joinpath(
                    f"{artist_data.name_slug}_{report_type}_beautified.tex"
                )
                with open(filename, "w") as f:
                    f.write(content)
                Logger.success(f"Saved beautified {report_type} to cache: {filename}")

        Logger.end_task(save_start, "Reports saved successfully")

        # Generate booking emails
        Logger.info("Starting booking email research")
        email_start = Logger.start_task("Booking email generation")
        emails_content = await generate_booking_emails(
            artist_data_raw, artist_data.name_slug
        )
        email_dir = cfg.get_path("email_dir", artist_data.name_slug)
        await save_emails_to_file(emails_content, artist_data.name_slug, email_dir)
        Logger.end_task(email_start, "Booking emails generated and saved")

        Logger.end_task(pipeline_start, "Full marketing pipeline completed")
        Logger.success(f"✅ All tasks completed for {artist_data.stage_name}")

    except Exception as e:
        Logger.error(f"Error in marketing pipeline: {str(e)}")
        raise


if __name__ == "__main__":
    import asyncio

    artist_id = "fdf3afd2-a3d8-462c-b2dc-7e0805573d03"
    asyncio.run(run_audiokit_ai_pipeline(artist_id))
