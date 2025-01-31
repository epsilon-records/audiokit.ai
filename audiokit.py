import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from datetime import date
import time
from datetime import datetime
import traceback

load_dotenv()  # Load environment variables from .env file

# API Configuration - Using os.getenv() with defaults where appropriate
SOUNDCHARTS_API_BASE = os.getenv("SOUNDCHARTS_API_BASE", "https://api.soundcharts.com")
SOUNDCHARTS_APP_ID = os.getenv("SOUNDCHARTS_APP_ID")
SOUNDCHARTS_API_KEY = os.getenv("SOUNDCHARTS_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Define custom headers
CUSTOM_HEADERS = {"HTTP-Referer": "https://audiokit.ai", "X-Title": "AudioKit"}

# EPK System Prompt
EPK_SYSTEM_PROMPT = """
You are an expert in electronic music industry marketing. Your task is to create a compelling Electronic Press Kit (EPK) from the provided JSON data. 

The EPK should be designed to attract booking agencies and event promoters and must be structured in Markdown format. Use clear headings, subheadings, and bullet points for professional presentation.

# EPK Structure

## 1. Artist Overview
- Craft a compelling one-paragraph pitch highlighting the artist's unique appeal
- Include genre focus, key achievements, and artistic direction
- Mention notable collaborations and remixes

## 2. Performance & Draw
- Current streaming numbers and growth trends
- Social media engagement metrics
- Geographic popularity insights

## 3. Recent Releases & Press
- Featured tracks from the past 12 months
- Remix work and collaborations
- Notable playlist inclusions or features

## 4. Stage Experience & Technical
- Performance style and format
- Technical rider highlights (if available)
- Past notable venues/events (if available)

## 5. Contact & Booking
- Management/booking contact details
- Social media and streaming links
- Website and press materials

# Formatting Guidelines
- Use proper Markdown syntax for headings, subheadings, and lists
- Maintain a professional, promotional tone throughout
- Focus on data points and achievements that demonstrate marketability
- Use bold text for emphasis where appropriate
- Ensure clear section organization and readability
- Keep the content concise and impactful

# Output Requirements
- The EPK must be in valid Markdown format
- Each section should be clearly separated
- Use consistent formatting throughout
- Ensure all information is accurate and derived from the provided data
"""

# Internal Report System Prompt
INTERNAL_REPORT_PROMPT = """
As a music industry analytics expert, create a comprehensive internal artist report from the provided JSON data. The report should be formatted in Markdown and structured with clear section headings, subheadings, and bullet points for readability. The report should provide actionable insights for the artist's strategic planning.

# Report Structure

## 1. Performance Analytics
- Detailed streaming metrics analysis across all platforms
- Month-over-month growth trends with percentage changes
- Platform-specific performance insights (e.g., Spotify, Apple Music, YouTube, TikTok)
- Comparative analysis against previous periods

## 2. Audience Development
- Follower growth rates across major platforms
- Engagement metrics and patterns (likes, comments, shares)
- Geographic distribution of listeners (top countries/cities)
- Platform-specific audience behavior (e.g., active hours, retention rates)

## 3. Release Impact Analysis
- Performance metrics for recent releases (stream counts, saves, playlist additions)
- Comparison of original tracks vs. remixes in terms of engagement and reach
- Collaboration impact on streaming numbers and audience crossover
- Effectiveness of release timing (day of the week, seasonal trends)

## 4. Distribution & Platform Strategy
- Platform-by-platform presence analysis (gaps, strengths)
- Identification of gaps in digital distribution
- Optimization opportunities for each streaming/social platform
- Content strategy recommendations based on past performance

## 5. Market Position Assessment
- Genre positioning (comparisons with similar artists)
- Competitive landscape (benchmarking against industry peers)
- Growth opportunities (new platforms, untapped audiences)
- Risk factors (declining metrics, audience shifts)

## 6. Action Items & Recommendations
- Short-term optimization steps (quick wins for immediate impact)
- Long-term strategic initiatives (sustained growth strategies)
- Platform-specific recommendations (e.g., ad spend allocation, content tweaks)
- Investment priorities (where to allocate marketing and production resources)

# Additional Formatting Guidelines:
- Use bold text for key metrics and insights
- Use code blocks if displaying raw data snippets
- Include tables for comparative analysis where applicable
- Use bullet points for easy readability
- Ensure concise, data-driven insights
"""

# Remove individual DB environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Add this near other configuration constants
AI_MODELS = [
    "deepseek/deepseek-r1",
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o-2024-11-20",
    "mistralai/mistral-large-2411",
]


class MarketingReport(BaseModel):
    artist_name: str = Field(..., description="Artist name")
    report: str = Field(..., description="Generated report content")
    budget_allocation: Dict[str, float] = Field(
        default_factory=dict, description="Budget allocation by category"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Strategic recommendations"
    )
    metrics: Dict[str, float] = Field(
        default_factory=dict, description="Key performance metrics"
    )


def display_artist_dashboard(artist_data: Dict):
    social_data = artist_data.get("current_stats", {}).get("social", {})  # ✅ FIXED
    social_df = pd.DataFrame(
        list(social_data.items()), columns=["Platform", "Followers"]
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(data=social_df, x="Platform", y="Followers", palette="Blues_d")
    plt.title("Artist Social Media Presence", fontsize=16)
    plt.xlabel("Social Media Platform", fontsize=12)
    plt.ylabel("Followers", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


class Logger:
    @staticmethod
    def info(message: str):
        print(f"ℹ️ [INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

    @staticmethod
    def success(message: str):
        print(
            f"✅ [SUCCESS] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}"
        )

    @staticmethod
    def warning(message: str):
        print(
            f"⚠️  [WARNING] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}"
        )

    @staticmethod
    def error(message: str):
        print(f"❌ [ERROR] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

    @staticmethod
    def start_task(message: str):
        print(f"⏳ [START] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")
        return time.time()

    @staticmethod
    def end_task(start_time: float, message: str):
        duration = time.time() - start_time
        print(
            f"🏁 [END] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message} (Duration: {duration:.2f}s)"
        )

    @staticmethod
    def progress(current: int, total: int, message: str):
        print(
            f"📊 [PROGRESS] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message} ({current}/{total} completed)"
        )


def sanitize_artist_data(artist_data):
    """Ensure artist data has no None values to prevent processing errors."""
    for key, value in artist_data.items():
        if value is None:
            if isinstance(value, int):
                artist_data[key] = 0
            elif isinstance(value, str):
                artist_data[key] = "N/A"
            elif isinstance(value, list):
                artist_data[key] = []
            elif isinstance(value, dict):
                artist_data[key] = {}
    return artist_data


def handle_report_error(
    e: Exception, model_name: str, artist_data: dict, report_type: str
) -> str:
    """Shared error handler for report generation functions"""
    error_details = {
        "error": str(e),
        "traceback": traceback.format_exc(),
        "model": model_name,
        "artist_data": artist_data.get("stage_name", "Unknown Artist"),
        "report_type": report_type,
    }
    Logger.warning(
        f"Failed to generate {report_type}: {json.dumps(error_details, indent=2)}"
    )
    return f"{report_type} generation failed: {str(e)}"


async def generate_epk(artist_data: dict, model_name: str) -> str:
    """Generate EPK using the specified model"""
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://audiokit.ai",
                "X-Title": "AudioKit",
            },
            json={
                "model": model_name,
                "messages": [
                    {"role": "system", "content": EPK_SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(artist_data)},
                ],
            },
            timeout=30,  # Add timeout
        )
        response.raise_for_status()
        response_data = response.json()
        if not response_data.get("choices") or not response_data["choices"][0].get(
            "message"
        ):
            raise ValueError("Invalid response structure from OpenRouter API")
        return response_data["choices"][0]["message"]["content"]
    except Exception as e:
        return handle_report_error(e, model_name, artist_data, "EPK")


async def generate_internal_report(artist_data: dict, model_name: str) -> str:
    """Generate internal report using the specified model"""
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://audiokit.ai",
                "X-Title": "AudioKit",
            },
            json={
                "model": model_name,
                "messages": [
                    {"role": "system", "content": INTERNAL_REPORT_PROMPT},
                    {"role": "user", "content": json.dumps(artist_data)},
                ],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return handle_report_error(e, model_name, artist_data, "Internal Report")


async def generate_reports(artist_data: dict):
    """Generate all reports using available models"""
    reports = {"EPK": {}, "Internal Report": {}}
    total_models = len(AI_MODELS)
    total_steps = (
        len(reports) * total_models
    )  # Calculate based on number of report types and models
    current_step = 0

    Logger.info(
        f"Starting report generation for {artist_data.get('stage_name', 'Unknown Artist')}"
    )
    Logger.info(f"Total models to process: {total_models}")
    Logger.info(f"Total steps to complete: {total_steps}")

    for model_name in AI_MODELS:
        current_step += 1
        Logger.info(f"Processing model {model_name} ({current_step}/{total_steps})")

        # Generate EPK
        Logger.info(f"Starting EPK generation with {model_name}")
        epk_start = Logger.start_task(f"EPK generation with {model_name}")
        epk_report = await generate_epk(artist_data, model_name)
        Logger.end_task(epk_start, f"Completed EPK generation with {model_name}")
        reports["EPK"][model_name] = epk_report
        Logger.success(f"EPK from {model_name} completed successfully")

        # Generate Internal Report
        current_step += 1
        Logger.info(
            f"Starting internal report generation with {model_name} ({current_step}/{total_steps})"
        )
        internal_start = Logger.start_task(
            f"Internal report generation with {model_name}"
        )
        internal_report = await generate_internal_report(artist_data, model_name)
        Logger.end_task(
            internal_start, f"Completed internal report generation with {model_name}"
        )
        reports["Internal Report"][model_name] = internal_report
        Logger.success(f"Internal report from {model_name} completed successfully")

    Logger.success(
        f"All report generation completed for {artist_data.get('stage_name', 'Unknown Artist')}"
    )
    return reports


async def select_best_strategy(reports: dict) -> dict:
    """Select and integrate the best strategy from multiple reports"""
    try:
        # Convert reports to JSON string for the prompt
        reports_json = json.dumps(reports)

        system_prompt = (
            "You are an expert music marketing strategist. You have received marketing reports "
            "from multiple AI models. Your task is to:\n"
            "1. Identify the best marketing strategy from these reports.\n"
            "2. Integrate the strongest insights from all reports into a single, optimized plan.\n"
            "3. Ensure the strategy is detailed, realistic, and well-budgeted.\n"
            "Respond in JSON format with keys: 'selected_model' (string), 'integrated_report' (string), and 'budget_allocation' (object of string:float)."
        )

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://audiokit.ai",
                "X-Title": "AudioKit",
            },
            json={
                "model": "deepseek/deepseek-r1",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": reports_json},
                ],
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        Logger.warning(f"Failed to select best strategy: {str(e)}")
        return {
            "selected_model": "None",
            "integrated_report": f"Strategy selection failed: {str(e)}",
            "budget_allocation": {},
        }


async def run_full_ai_marketing_pipeline(artist_id: str):
    """Run the full marketing pipeline"""
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

        # Select best strategy
        Logger.info("Starting strategy selection process")
        strategy_start = Logger.start_task("Strategy selection")
        best_strategy = await select_best_strategy(all_reports)
        Logger.end_task(strategy_start, "Strategy selection completed")
        Logger.success("Best strategy selected and integrated")

        # Save reports
        Logger.info("Starting report saving process")
        save_start = Logger.start_task("Saving reports")
        artist_name_slug = artist_data["stage_name"].replace(" ", "_")

        # Save individual reports
        total_reports = sum(len(models) for models in all_reports.values())
        saved_reports = 0
        for report_type, models in all_reports.items():
            for model_name, content in models.items():
                saved_reports += 1
                filename = f"{artist_name_slug}_{report_type}_{model_name.replace('/', '_')}.md"
                Logger.info(
                    f"Saving {report_type} from {model_name} ({saved_reports}/{total_reports})"
                )
                with open(filename, "w") as f:
                    f.write(content)
                Logger.success(f"Saved {filename} successfully")

        # Save integrated strategy
        strategy_filename = f"{artist_name_slug}_integrated_strategy.json"
        Logger.info(f"Saving integrated strategy to {strategy_filename}")
        with open(strategy_filename, "w") as f:
            json.dump(best_strategy, f, indent=2)
        Logger.end_task(save_start, "All reports saved successfully")
        Logger.success(f"Integrated strategy saved to {strategy_filename}")

        # Display dashboard
        Logger.info("Displaying artist dashboard")
        display_start = Logger.start_task("Displaying dashboard")
        display_artist_dashboard(artist_data)
        Logger.end_task(display_start, "Dashboard displayed successfully")

        Logger.end_task(pipeline_start, "Full marketing pipeline completed")
        Logger.success(f"✅ All tasks completed for {artist_data['stage_name']}")

    except Exception as e:
        Logger.error(f"Error in marketing pipeline: {str(e)}")
        raise


def get_artist_data_from_db(artist_id: str) -> dict:
    db_start = Logger.start_task(f"Fetching artist data for ID {artist_id}")
    connection = None
    try:
        Logger.info("Connecting to database")
        connect_start = Logger.start_task("Database connection")
        connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        Logger.end_task(connect_start, "Database connected successfully")

        with connection.cursor() as cursor:
            Logger.info("Executing database query")
            query = "SELECT * FROM artists WHERE id = %s"
            cursor.execute(query, (artist_id,))
            result = cursor.fetchone()

            if not result:
                Logger.error(f"Artist with ID {artist_id} not found")
                raise ValueError(f"Artist with ID {artist_id} not found")

            Logger.info("Processing database result")
            artist_data = dict(result)
            for key, value in artist_data.items():
                if isinstance(value, date):
                    artist_data[key] = value.isoformat()

            Logger.info("Saving artist data to JSON file")
            artist_name_slug = artist_data["stage_name"].replace(" ", "_")
            with open(f"{artist_name_slug}_json.txt", "w") as json_file:
                json.dump(artist_data, json_file, indent=2)
            Logger.success(f"Artist data saved to {artist_name_slug}_json.txt")

            Logger.end_task(db_start, "Database operation completed")
            return artist_data

    except Exception as e:
        Logger.error(f"Database error: {str(e)}")
        raise Exception(f"Database error: {str(e)}")
    finally:
        if connection:
            Logger.info("Closing database connection")
            connection.close()
            Logger.success("Database connection closed")


if __name__ == "__main__":
    import asyncio

    artist_id = "fdf3afd2-a3d8-462c-b2dc-7e0805573d03"
    asyncio.run(run_full_ai_marketing_pipeline(artist_id))
