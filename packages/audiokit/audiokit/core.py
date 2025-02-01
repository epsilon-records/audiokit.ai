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


async def run_audiokit_ai_pipeline(artist_id: str):
    """Run the full AI-powered marketing pipeline for artists"""
    pipeline_start = Logger.start_task("Starting full marketing pipeline")
    try:
        Logger.info(f"Starting pipeline for artist ID: {artist_id}")

        # Fetch artist data
        Logger.info("Fetching artist data from database")
        fetch_start = Logger.start_task("Fetching artist data")
        artist_data = get_artist_data_from_db(artist_id)
        Logger.end_task(fetch_start, "Artist data fetched successfully")
        Logger.info(
            f"Artist data retrieved for: {artist_data.get('stage_name', 'Unknown Artist')}"
        )

        # Generate reports
        Logger.info("Starting report generation process")
        report_start = Logger.start_task("Report generation")
        all_reports = await generate_reports(artist_data)
        Logger.end_task(report_start, "Report generation completed")
        Logger.success(
            f"Generated {len(all_reports['EPK'])} EPKs and {len(all_reports['Internal Report'])} internal reports"
        )

        # Integrate and optimize reports with dependency tracking
        Logger.info("Starting report integration process")
        strategy_start = Logger.start_task("Report integration")
        artist_name_slug = artist_data["stage_name"].replace(" ", "-").lower()
        integrated_reports = await integrate_reports(all_reports, artist_name_slug)
        Logger.end_task(strategy_start, "Report integration completed")
        Logger.success("Reports integrated and optimized")

        # Beautify reports
        Logger.info("Starting report beautification process")
        beautify_start = Logger.start_task("Report beautification")

        # Beautify EPK
        if integrated_reports["EPK"]:
            epk_beautify_start = Logger.start_task("EPK beautification")
            integrated_reports["EPK"] = await beautify_report(
                integrated_reports["EPK"], "EPK", artist_name_slug
            )
            Logger.end_task(epk_beautify_start, "EPK beautification completed")

        # Beautify Internal Report
        if integrated_reports["Internal Report"]:
            internal_beautify_start = Logger.start_task(
                "Internal Report beautification"
            )
            integrated_reports["Internal Report"] = await beautify_report(
                integrated_reports["Internal Report"],
                "Internal Report",
                artist_name_slug,
            )
            Logger.end_task(
                internal_beautify_start, "Internal Report beautification completed"
            )

        Logger.end_task(beautify_start, "Report beautification completed")
        Logger.success("Reports beautified successfully")

        # Save reports
        Logger.info("Starting report saving process")
        save_start = Logger.start_task("Saving reports")
        cache_dir = cfg.get_path("cache_dir", artist_name_slug)

        # Save beautified reports to cache
        Logger.info("Saving beautified reports to cache")
        os.makedirs(cache_dir, exist_ok=True)

        if integrated_reports["EPK"]:
            epk_filename = cache_dir.joinpath(
                f"{artist_name_slug}_integrated_epk_beautified.tex"
            )
            with open(epk_filename, "w") as f:
                f.write(integrated_reports["EPK"])
            Logger.success(f"Saved beautified EPK to cache: {epk_filename}")

        if integrated_reports["Internal Report"]:
            internal_filename = cache_dir.joinpath(
                f"{artist_name_slug}_integrated_internal_report_beautified.tex",
            )
            with open(internal_filename, "w") as f:
                f.write(integrated_reports["Internal Report"])
            Logger.success(
                f"Saved beautified internal report to cache: {internal_filename}"
            )

        Logger.end_task(save_start, "Reports saved successfully")

        # Generate booking emails
        Logger.info("Starting booking email research")
        email_start = Logger.start_task("Booking email generation")
        emails_content = await generate_booking_emails(artist_data, artist_name_slug)
        email_dir = cfg.get_path("email_dir", artist_name_slug)
        await save_emails_to_file(emails_content, artist_name_slug, email_dir)
        Logger.end_task(email_start, "Booking emails generated and saved")

        Logger.end_task(pipeline_start, "Full marketing pipeline completed")
        Logger.success(f"✅ All tasks completed for {artist_data['stage_name']}")

    except Exception as e:
        Logger.error(f"Error in marketing pipeline: {str(e)}")
        raise


if __name__ == "__main__":
    import asyncio

    artist_id = "fdf3afd2-a3d8-462c-b2dc-7e0805573d03"
    asyncio.run(run_audiokit_ai_pipeline(artist_id))
