import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from datetime import date
import httpx
import time
from datetime import datetime
import asyncio

load_dotenv()  # Load environment variables from .env file

# API Configuration - Using os.getenv() with defaults where appropriate
SOUNDCHARTS_API_BASE = os.getenv("SOUNDCHARTS_API_BASE", "https://api.soundcharts.com")
SOUNDCHARTS_APP_ID = os.getenv("SOUNDCHARTS_APP_ID")
SOUNDCHARTS_API_KEY = os.getenv("SOUNDCHARTS_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Define custom headers
CUSTOM_HEADERS = {"HTTP-Referer": "https://audiokit.ai", "X-Title": "AudioKit"}

# Create async client with custom headers
async_client = httpx.AsyncClient(headers=CUSTOM_HEADERS)

# Initialize single DeepSeek model
ai_model = OpenAIModel(
    model_name="deepseek/deepseek-r1",
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    http_client=async_client,
)

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

# Update the agents to use the single model
epk_agent = Agent(
    model=ai_model,
    system_prompt=EPK_SYSTEM_PROMPT,
    result_type=str,
)

internal_report_agent = Agent(
    model=ai_model,
    system_prompt=INTERNAL_REPORT_PROMPT,
    result_type=str,
)

market_analysis_agent = Agent(
    model=ai_model,
    system_prompt="You are a strategic music marketing expert...",
    result_type=str,
)

strategy_selection_agent = Agent(
    model=ai_model,
    system_prompt=(
        "You are an expert music marketing strategist. You have received marketing reports "
        "from multiple AI models. Your task is to:\n"
        "1. Identify the best marketing strategy from these reports.\n"
        "2. Integrate the strongest insights from all reports into a single, optimized plan.\n"
        "3. Ensure the strategy is detailed, realistic, and well-budgeted.\n"
        "Respond in JSON format with keys: 'selected_model' (string), 'integrated_report' (string), and budget_allocation' (object of string:float)."
    ),
    result_type=dict,
)

# Add this near other configuration constants
AI_MODELS = [
    "deepseek/deepseek-r1",
    "anthropic/claude-3-opus",
    "openai/o1",
    "mistral/mistral-large",
]


class ArtistData(BaseModel):
    name: str = Field("Unknown Artist", description="Artist name")
    genre: str = Field("Unknown Genre", description="Primary genre")
    monthly_streams: int = Field(0, description="Monthly streaming count")
    social_media_followers: Dict[str, int] = Field(
        default_factory=dict, description="Social media followers by platform"
    )
    top_countries: List[str] = Field(
        default_factory=list, description="Top countries by listenership"
    )
    recent_releases: List[str] = Field(
        default_factory=list, description="Recent release titles"
    )
    collaboration_artists: List[str] = Field(
        default_factory=list, description="List of collaborating artists"
    )
    marketing_budget: float = Field(0.0, description="Marketing budget in USD")
    biography: Optional[str] = Field(None, description="Artist biography")
    image_url: Optional[str] = Field(None, description="URL to artist image")
    genres: Optional[List[Dict[str, List[str]]]] = Field(
        None, description="Detailed genre information"
    )
    country_code: Optional[str] = Field(None, description="ISO country code")
    # Add any other fields that are commonly used


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


async def generate_report_with_agent(
    agent, artist_data: dict, report_type: str, model_name: str, reports: dict
):
    start_time = Logger.start_task(f"Generating {report_type} with {model_name}")
    try:
        agent.model.model_name = model_name  # Update just the model name
        artist_data = sanitize_artist_data(artist_data)
        result = await agent.run(json.dumps(artist_data))

        if result is None or result.data is None:
            raise ValueError(f"{report_type} generation returned None for {model_name}")

        reports[report_type][model_name] = result.data
        Logger.success(f"{report_type} generated successfully with {model_name}")

    except Exception as e:
        Logger.warning(f"Failed to generate {report_type} with {model_name}: {str(e)}")
        reports[report_type][model_name] = f"{report_type} generation failed: {str(e)}"
    finally:
        Logger.end_task(start_time, f"Completed {report_type} with {model_name}")


def generate_reports(artist_data: dict):
    reports = {"EPK": {}, "Internal Report": {}, "Market Analysis": {}}
    total_models = len(AI_MODELS)

    for current_model, model_name in enumerate(AI_MODELS, 1):
        Logger.progress(current_model, total_models, f"Processing model {model_name}")

        # Generate reports using helper function
        await generate_report_with_agent(
            epk_agent, artist_data, "EPK", model_name, reports
        )
        await generate_report_with_agent(
            internal_report_agent, artist_data, "Internal Report", model_name, reports
        )
        await generate_report_with_agent(
            market_analysis_agent, artist_data, "Market Analysis", model_name, reports
        )

    Logger.success("All report attempts completed")
    return reports


def run_full_ai_marketing_pipeline(artist_id: str):
    pipeline_start = Logger.start_task("Starting full marketing pipeline")
    try:
        Logger.info("Fetching artist data from database")
        artist_data = get_artist_data_from_db(artist_id)

        Logger.info("Generating reports")
        all_reports = await generate_reports(artist_data)
        Logger.success("Report generation completed")

        Logger.info("Running strategy selection")
        strategy_start = Logger.start_task("Running strategy selection agent")
        try:
            strategy_result = strategy_selection_agent.run_sync(
                json.dumps(all_reports, indent=2)
            )
            integrated_strategy = strategy_result.data
            Logger.success("Strategy selection completed")
        except Exception as e:
            Logger.warning(f"Strategy selection failed: {str(e)}")
            # Fallback to selecting the first successful report from each category
            integrated_strategy = {
                "EPK": next(
                    (
                        report
                        for report in all_reports["EPK"].values()
                        if "failed" not in str(report)
                    ),
                    "No successful EPK generated",
                ),
                "Internal Report": next(
                    (
                        report
                        for report in all_reports["Internal Report"].values()
                        if "failed" not in str(report)
                    ),
                    "No successful Internal Report generated",
                ),
                "Market Analysis": next(
                    (
                        report
                        for report in all_reports["Market Analysis"].values()
                        if "failed" not in str(report)
                    ),
                    "No successful Market Analysis generated",
                ),
            }
        finally:
            Logger.end_task(strategy_start, "Strategy selection process completed")

        Logger.info("Extracting best reports")
        best_epk_report = integrated_strategy.get("EPK", "No EPK generated.")
        best_internal_report = integrated_strategy.get(
            "Internal Report", "No Internal Report generated."
        )
        best_market_analysis = integrated_strategy.get(
            "Market Analysis", "No Market Analysis generated."
        )

        Logger.info("Saving reports to files")
        artist_name_slug = artist_data["stage_name"].replace(" ", "_")

        with open(f"{artist_name_slug}_epk.md", "w") as epk_file:
            epk_file.write(best_epk_report)
        Logger.success(f"EPK saved to {artist_name_slug}_epk.md")

        with open(f"{artist_name_slug}_internal.md", "w") as internal_file:
            internal_file.write(best_internal_report)
        Logger.success(f"Internal report saved to {artist_name_slug}_internal.md")

        with open(f"{artist_name_slug}_market_analysis.md", "w") as market_file:
            market_file.write(best_market_analysis)
        Logger.success(
            f"Market analysis saved to {artist_name_slug}_market_analysis.md"
        )

        Logger.info("Displaying artist dashboard")
        display_artist_dashboard(artist_data)
        Logger.success("Dashboard displayed successfully")

        Logger.end_task(pipeline_start, "Full marketing pipeline completed")
        Logger.success(
            f"✅ Reports generated and saved for {artist_data['stage_name']}"
        )

    except Exception as e:
        Logger.error(f"Error in marketing pipeline: {str(e)}")
        raise


def get_artist_data_from_db(artist_id: str) -> dict:
    db_start = Logger.start_task(f"Fetching artist data for ID {artist_id}")
    connection = None
    try:
        Logger.info("Connecting to database")
        connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

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


async def main():
    artist_id = "fdf3afd2-a3d8-462c-b2dc-7e0805573d03"
    await run_full_ai_marketing_pipeline(artist_id)


if __name__ == "__main__":
    asyncio.run(main())
