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
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from datetime import date
import httpx
import time
from datetime import datetime

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

# Initialize models using OpenRouter
AI_MODELS = {
    "Claude 3 Opus": OpenAIModel(
        model_name="anthropic/claude-3-opus",
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        http_client=async_client,
    ),
    "Mistral Large 2411": OpenAIModel(
        model_name="mistralai/mistral-large-2411",
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        http_client=async_client,
    ),
    "DeepSeek-R1": OpenAIModel(
        model_name="deepseek/deepseek-r1",
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        http_client=async_client,
    ),
    "OpenAI O1": OpenAIModel(
        model_name="openai/o1",
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        http_client=async_client,
    ),
}


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

# Define the EPK Agent
epk_agent = Agent(
    model=AI_MODELS["DeepSeek-R1"],
    system_prompt=EPK_SYSTEM_PROMPT,
    result_type=str,  # Assuming the result is a Markdown string
)

# Define the Internal Report Agent
internal_report_agent = Agent(
    model=AI_MODELS["DeepSeek-R1"],
    system_prompt=INTERNAL_REPORT_PROMPT,
    result_type=str,  # Assuming the result is a Markdown string
)

market_analysis_agent = Agent(
    model=AI_MODELS["DeepSeek-R1"],  # Will be set dynamically
    system_prompt="You are a strategic music marketing expert. Generate a market analysis report...",
    result_type=str,
)

# Define the Strategy Selection Agent
strategy_selection_agent = Agent(
    model=AI_MODELS["DeepSeek-R1"],
    system_prompt=(
        "You are an expert music marketing strategist. You have received marketing reports "
        "from multiple AI models. Your task is to:\n"
        "1. Identify the best marketing strategy from these reports.\n"
        "2. Integrate the strongest insights from all reports into a single, optimized plan.\n"
        "3. Ensure the strategy is detailed, realistic, and well-budgeted.\n"
        "Respond in JSON format with keys: 'selected_model' (string), 'integrated_report' (string), and 'budget_allocation' (object of string:float)."
    ),
    result_type=dict,  # Assuming the result is a JSON object
)


# Example tool to fetch additional artist data
@epk_agent.tool
async def fetch_additional_data(ctx: RunContext, artist_id: str) -> dict:
    # Implement the logic to fetch additional data based on artist_id
    return {"additional_info": "Sample data"}


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


def generate_reports(json_data: dict):
    reports = {"EPK": {}, "Internal Report": {}, "Market Analysis": {}}
    total_models = len(AI_MODELS)
    current_model = 0

    for model_name, model_id in AI_MODELS.items():
        current_model += 1
        Logger.progress(current_model, total_models, f"Processing model {model_name}")

        # Generate EPK Report
        epk_start = Logger.start_task(f"Generating EPK with {model_name}")
        epk_agent.model = model_id
        try:
            epk_result = epk_agent.run_sync(json.dumps(json_data, indent=2))
            reports["EPK"][model_name] = epk_result.data
            Logger.success(f"EPK generated successfully with {model_name}")
        except Exception as e:
            Logger.warning(f"Failed to generate EPK with {model_name}: {str(e)}")
            reports["EPK"][model_name] = f"EPK generation failed: {str(e)}"
        finally:
            Logger.end_task(epk_start, f"Completed EPK with {model_name}")

        # Generate Internal Report
        internal_start = Logger.start_task(
            f"Generating Internal Report with {model_name}"
        )
        internal_report_agent.model = model_id
        try:
            internal_report_result = internal_report_agent.run_sync(
                json.dumps(json_data, indent=2)
            )
            reports["Internal Report"][model_name] = internal_report_result.data
            Logger.success(f"Internal Report generated successfully with {model_name}")
        except Exception as e:
            Logger.warning(
                f"Failed to generate Internal Report with {model_name}: {str(e)}"
            )
            reports["Internal Report"][model_name] = (
                f"Internal Report generation failed: {str(e)}"
            )
        finally:
            Logger.end_task(
                internal_start, f"Completed Internal Report with {model_name}"
            )

        # Generate Market Analysis Report
        market_start = Logger.start_task(
            f"Generating Market Analysis with {model_name}"
        )
        market_analysis_agent.model = model_id
        try:
            market_analysis_result = market_analysis_agent.run_sync(
                json.dumps(json_data, indent=2)
            )
            reports["Market Analysis"][model_name] = market_analysis_result.data
            Logger.success(f"Market Analysis generated successfully with {model_name}")
        except Exception as e:
            Logger.warning(
                f"Failed to generate Market Analysis with {model_name}: {str(e)}"
            )
            reports["Market Analysis"][model_name] = (
                f"Market Analysis generation failed: {str(e)}"
            )
        finally:
            Logger.end_task(
                market_start, f"Completed Market Analysis with {model_name}"
            )

    Logger.success("All report attempts completed")
    return reports


def run_full_ai_marketing_pipeline(json_data: Dict):
    pipeline_start = Logger.start_task("Starting full marketing pipeline")
    try:
        Logger.info("Validating artist data")
        artist_info = ArtistData(**json_data)
        Logger.success("Artist data validated successfully")

        Logger.info("Generating reports")
        all_reports = generate_reports(json_data)
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
        artist_name_slug = artist_info.name.replace(" ", "_")

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
        display_artist_dashboard(artist_info.dict())
        Logger.success("Dashboard displayed successfully")

        Logger.end_task(pipeline_start, "Full marketing pipeline completed")
        Logger.success(f"✅ Reports generated and saved for {artist_info.name}")

    except Exception as e:
        Logger.error(f"Error in marketing pipeline: {str(e)}")
        raise


def get_artist_data_from_db(artist_id: str) -> Dict:
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


# Updated example usage:
artist_id = "fdf3afd2-a3d8-462c-b2dc-7e0805573d03"  # This should come from your application logic
json_data = get_artist_data_from_db(artist_id)
run_full_ai_marketing_pipeline(json_data)
