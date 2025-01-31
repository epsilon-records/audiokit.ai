import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Type
from pydantic import BaseModel, Field, create_model, ValidationError
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic_ai import Agent, RunContext

load_dotenv()  # Load environment variables from .env file

# API Configuration - Using os.getenv() with defaults where appropriate
SOUNDCHARTS_API_BASE = os.getenv("SOUNDCHARTS_API_BASE", "https://api.soundcharts.com")
SOUNDCHARTS_APP_ID = os.getenv("SOUNDCHARTS_APP_ID")
SOUNDCHARTS_API_KEY = os.getenv("SOUNDCHARTS_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# AI Models
AI_MODELS = {
    "GPT-4 Turbo": "openai/gpt-4-turbo",
    "Claude 3 Opus": "anthropic/claude-3-opus",
    "Mistral Large": "mistralai/mistral-large-latest",
    "DeepSeek-R1": "deepseek/deepseek-r1",  # ✅ Added DeepSeek-R1
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
    model="openai:gpt-4-turbo",
    system_prompt=EPK_SYSTEM_PROMPT,
    result_type=str,  # Assuming the result is a Markdown string
)

# Define the Internal Report Agent
internal_report_agent = Agent(
    model="openai:gpt-4-turbo",
    system_prompt=INTERNAL_REPORT_PROMPT,
    result_type=str,  # Assuming the result is a Markdown string
)

market_analysis_agent = Agent(
    model="",  # Will be set dynamically
    system_prompt="You are a strategic music marketing expert. Generate a market analysis report...",
    result_type=str,
)

# Define the Strategy Selection Agent
strategy_selection_agent = Agent(
    model="openai/gpt-4-turbo",
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


def create_dynamic_artist_model(data: Dict) -> Type[BaseModel]:
    """Dynamically creates an ArtistData model based on the input data structure"""
    fields = {
        "name": (str, Field(..., description="Artist name")),
        "genre": (str, Field(..., description="Primary genre")),
        "monthly_streams": (int, Field(0, description="Monthly streaming count")),
        "social_media_followers": (
            Dict[str, int],
            Field(
                default_factory=dict, description="Social media followers by platform"
            ),
        ),
        "top_countries": (
            List[str],
            Field(default_factory=list, description="Top countries by listenership"),
        ),
        "recent_releases": (
            List[str],
            Field(default_factory=list, description="Recent release titles"),
        ),
        "collaboration_artists": (
            List[str],
            Field(default_factory=list, description="List of collaborating artists"),
        ),
        "marketing_budget": (float, Field(0.0, description="Marketing budget in USD")),
    }

    # Add optional fields based on data presence
    if "biography" in data:
        fields["biography"] = (
            Optional[str],
            Field(None, description="Artist biography"),
        )
    if "image_url" in data:
        fields["image_url"] = (
            Optional[str],
            Field(None, description="URL to artist image"),
        )
    if "genres" in data:
        fields["genres"] = (
            Optional[List[Dict[str, List[str]]]],
            Field(None, description="Detailed genre information"),
        )
    if "country_code" in data:
        fields["country_code"] = (
            Optional[str],
            Field(None, description="ISO country code"),
        )

    return create_model("DynamicArtistData", **fields)


def create_dynamic_report_model(data: Dict) -> Type[BaseModel]:
    """Dynamically creates a MarketingReport model based on the input data structure"""
    fields = {
        "artist_name": (str, Field(..., description="Artist name")),
        "report": (str, Field(..., description="Generated report content")),
        "budget_allocation": (
            Dict[str, float],
            Field(default_factory=dict, description="Budget allocation by category"),
        ),
    }

    # Add additional fields if present in data
    if "recommendations" in data:
        fields["recommendations"] = (
            List[str],
            Field(default_factory=list, description="Strategic recommendations"),
        )
    if "metrics" in data:
        fields["metrics"] = (
            Dict[str, float],
            Field(default_factory=dict, description="Key performance metrics"),
        )

    return create_model("DynamicMarketingReport", **fields)


def generate_internal_report(artist_data: Dict, model_name: str) -> Type[BaseModel]:
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": AI_MODELS[model_name],
                "messages": [
                    {"role": "system", "content": INTERNAL_REPORT_PROMPT},
                    {"role": "user", "content": json.dumps(artist_data, indent=2)},
                ],
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        response_data = response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    try:
        report_content = json.loads(response_data["choices"][0]["message"]["content"])
        ReportModel = create_dynamic_report_model(report_content)
        return ReportModel(
            artist_name=artist_data["name"],
            report=report_content.get("report", "No detailed report generated"),
            budget_allocation=report_content.get("budget_allocation", {}),
        )
    except (json.JSONDecodeError, KeyError, ValidationError) as e:
        raise Exception(f"Failed to parse or validate report: {str(e)}")


# EPK Report Generation
def generate_epk_report(artist_data: Dict, model_name: str) -> Type[BaseModel]:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": AI_MODELS[model_name],
            "messages": [
                {"role": "system", "content": EPK_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(artist_data, indent=2)},
            ],
            "response_format": {"type": "json_object"},
        },
    ).json()
    try:
        report_content = json.loads(response["choices"][0]["message"]["content"])
        ReportModel = create_dynamic_report_model(report_content)
        return ReportModel(
            artist_name=artist_data["name"],
            report=report_content.get("report", "No detailed report generated"),
            budget_allocation=report_content.get("budget_allocation", {}),
        )
    except (json.JSONDecodeError, KeyError, ValidationError) as e:
        raise Exception(f"Failed to parse or validate report: {str(e)}")


# AI Decision Making (Select Best Strategy & Merge Insights)
def select_best_strategy(reports: Dict[str, BaseModel]) -> BaseModel:
    evaluation_prompt = (
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
            "Content-Type": "application/json",
        },
        json={
            "model": AI_MODELS["GPT-4 Turbo"],
            "messages": [
                {"role": "system", "content": evaluation_prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {model: report.dict() for model, report in reports.items()},
                        indent=2,
                    ),
                },
            ],
            "response_format": {"type": "json_object"},
        },
    ).json()

    response_data = json.loads(response["choices"][0]["message"]["content"])
    ReportModel = create_dynamic_report_model(response_data)
    return ReportModel(
        artist_name=response_data.get("artist_name", "Unknown Artist"),
        report=response_data.get(
            "integrated_report", "No integrated strategy generated."
        ),
        budget_allocation=response_data.get("budget_allocation", {}),
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


def generate_reports(json_data: dict):
    reports = {"EPK": {}, "Internal Report": {}, "Market Analysis": {}}

    for model_name, model_id in AI_MODELS.items():
        print(f"Generating reports with {model_name}...")

        # Generate EPK Report
        epk_agent.model = model_id
        epk_result = epk_agent.run_sync(json.dumps(json_data, indent=2))
        reports["EPK"][model_name] = epk_result.data

        # Generate Internal Report
        internal_report_agent.model = model_id
        internal_report_result = internal_report_agent.run_sync(
            json.dumps(json_data, indent=2)
        )
        reports["Internal Report"][model_name] = internal_report_result.data

        # Generate Market Analysis Report
        market_analysis_agent.model = model_id  # ✅ FIXED
        market_analysis_result = market_analysis_agent.run_sync(
            json.dumps(json_data, indent=2)
        )
        reports["Market Analysis"][model_name] = market_analysis_result.data

    return reports


def run_full_ai_marketing_pipeline(json_data: Dict):
    ArtistModel = create_dynamic_artist_model(json_data)
    artist_info = ArtistModel(**json_data)

    # Generate all reports using multiple AI models
    all_reports = generate_reports(json_data)

    # Run the Strategy Selection Agent
    strategy_result = strategy_selection_agent.run_sync(
        json.dumps(all_reports, indent=2)
    )
    integrated_strategy = strategy_result.data

    # Extract best reports (SAFELY)
    best_epk_report = integrated_strategy.get("EPK", "No EPK generated.")
    best_internal_report = integrated_strategy.get(
        "Internal Report", "No Internal Report generated."
    )
    best_market_analysis = integrated_strategy.get(
        "Market Analysis", "No Market Analysis generated."
    )

    # Write reports to files
    artist_name_slug = artist_info.name.replace(" ", "_")

    with open(f"{artist_name_slug}_epk.md", "w") as epk_file:
        epk_file.write(best_epk_report)  # ✅ FIXED

    with open(f"{artist_name_slug}_internal.md", "w") as internal_file:
        internal_file.write(best_internal_report)  # ✅ FIXED

    with open(f"{artist_name_slug}_market_analysis.md", "w") as market_file:
        market_file.write(best_market_analysis)  # ✅ FIXED

    # Display the artist dashboard
    display_artist_dashboard(artist_info.dict())

    print(f"✅ Reports generated and saved for {artist_info.name}")


def get_artist_data_from_db(artist_id: str) -> Dict:
    connection = None
    try:
        connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

        with connection.cursor() as cursor:
            query = "SELECT * FROM artists WHERE id = %s"
            cursor.execute(query, (artist_id,))
            result = cursor.fetchone()

            if not result:
                raise ValueError(f"Artist with ID {artist_id} not found")

            # Convert to dictionary and write to JSON file
            artist_data = dict(result)
            artist_name_slug = artist_data["name"].replace(" ", "_")
            with open(f"{artist_name_slug}_json.txt", "w") as json_file:
                json.dump(artist_data, json_file, indent=2)

            return artist_data

    except Exception as e:
        raise Exception(f"Database error: {str(e)}")
    finally:
        if connection:
            connection.close()


# Updated example usage:
artist_id = "fdf3afd2-a3d8-462c-b2dc-7e0805573d03"  # This should come from your application logic
json_data = get_artist_data_from_db(artist_id)
run_full_ai_marketing_pipeline(json_data)
