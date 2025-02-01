import json
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
You are an expert in electronic music industry marketing. Using the provided JSON data, generate a comprehensive and visually appealing Electronic Press Kit (EPK).

Report Requirements:
	1.	Professional Formatting: Use clear section headings, subheadings, and bullet points for readability
	2.	Aesthetic Design: Create a polished and visually appealing layout with proper spacing and alignment
	3.	Compelling Content: Highlight key selling points, artist branding, and achievements to captivate promoters
	4.	Visual Enhancements: Use emojis sparingly to enhance key points (1-2 per section max)

Output Instructions:
	• Maintain a professional tone while being approachable
	• Do not include any backticks, code block markers, or other syntax wrappers
	• Do not wrap the output in JSON blocks or any other formatting
	• Output must be plain text with the formatted content only

EPK Structure:

# 🎤 Artist Overview
- Craft a compelling one-paragraph pitch highlighting the artist's unique appeal
- Include genre focus, key achievements, and artistic direction
- Mention notable collaborations and remixes

# 📊 Performance & Draw
- Current streaming numbers and growth trends
- Social media engagement metrics
- Geographic popularity insights

# 🎧 Recent Releases & Press
- Featured tracks from the past 12 months
- Remix work and collaborations
- Notable playlist inclusions or features

# 🎪 Stage Experience & Technical
- Performance style and format
- Technical rider highlights (if available)
- Past notable venues/events (if available)

# 📞 Contact & Booking
- Management/booking contact details
- Social media and streaming links
- Website and press materials
"""

# Internal Report System Prompt
INTERNAL_REPORT_PROMPT = """
You are a music industry analytics expert. Using the provided JSON data, generate a comprehensive and visually appealing internal artist report.

Report Requirements:
	1.	Professional Formatting: Use clear section headings, subheadings, and bullet points for readability
	2.	Aesthetic Design: Create a polished and visually appealing layout with proper spacing and alignment
	3.	Compelling Content: Highlight key selling points, artist branding, and achievements
	4.	Visual Enhancements: Use emojis sparingly to enhance key points (1-2 per section max)

Output Instructions:
	• Maintain a professional tone while being approachable
	• Do not include any backticks, code block markers, or other syntax wrappers
	• Do not wrap the output in JSON blocks or any other formatting
	• Output must be plain text with the formatted content only

Report Structure:

# 📈 Performance Analytics
- Detailed streaming metrics analysis across all platforms
- Month-over-month growth trends with percentage changes
- Platform-specific performance insights (e.g., Spotify, Apple Music, YouTube, TikTok)
- Comparative analysis against previous periods

# 🌍 Audience Development
- Follower growth rates across major platforms
- Engagement metrics and patterns (likes, comments, shares)
- Geographic distribution of listeners (top countries/cities)
- Platform-specific audience behavior (e.g., active hours, retention rates)

# 🎵 Release Impact Analysis
- Performance metrics for recent releases (stream counts, saves, playlist additions)
- Comparison of original tracks vs. remixes in terms of engagement and reach
- Collaboration impact on streaming numbers and audience crossover
- Effectiveness of release timing (day of the week, seasonal trends)

# 📱 Distribution & Platform Strategy
- Platform-by-platform presence analysis (gaps, strengths)
- Identification of gaps in digital distribution
- Optimization opportunities for each streaming/social platform
- Content strategy recommendations based on past performance

# 🏆 Market Position Assessment
- Genre positioning (comparisons with similar artists)
- Competitive landscape (benchmarking against industry peers)
- Growth opportunities (new platforms, untapped audiences)
- Risk factors (declining metrics, audience shifts)

# 🚀 Action Items & Recommendations
- Short-term optimization steps (quick wins for immediate impact)
- Long-term strategic initiatives (sustained growth strategies)
- Platform-specific recommendations (e.g., ad spend allocation, content tweaks)
- Investment priorities (where to allocate marketing and production resources)
"""

# Remove individual DB environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Add this near other configuration constants
AI_MODELS = [
    "deepseek/deepseek-chat",
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o-2024-11-20",
]

# Constants for report integration
EPK_INTEGRATION_MODEL = "anthropic/claude-3.5-sonnet"
INTERNAL_REPORT_INTEGRATION_MODEL = "anthropic/claude-3.5-sonnet"

EPK_INTEGRATION_PROMPT = """
You are an expert music marketing strategist and professional document designer. You will receive multiple EPK reports from AI models. Your task is to generate a professionally formatted, publication-ready LaTeX document by following these steps:

Processing Steps:
1. Integrate Valuable Insights: Extract and incorporate useful data, insights, or recommendations from the other reports to enhance the final version
2. Eliminate Redundancies: Remove repetitive or unnecessary information to ensure clarity and conciseness
3. Finalize for Publication: Replace any placeholders, refine the language, and structure the document to be visually appealing and professionally formatted in LaTeX

Output Requirements:
• Do not wrap the content in any code blocks or markdown syntax
• Maintain a strictly formal and professional tone
• Use emojis strategically to enhance visual appeal and engagement

LaTeX Document Structure:
\\documentclass{article}
\\usepackage{fontspec}
\\usepackage{emoji}
\\setmainfont{Noto Color Emoji}
\\begin{document}

EPK Structure Requirements:
# 🎤 Artist Overview
- Craft a compelling one-paragraph pitch
- Highlight unique selling points and artistic vision
- Include genre focus and key achievements

# 📊 Performance & Draw
- Current streaming numbers and growth trends
- Social media engagement metrics
- Geographic popularity insights

# 🎧 Recent Releases & Press
- Featured tracks from the past 12 months
- Remix work and collaborations
- Notable playlist inclusions or features

# 🎪 Stage Experience & Technical
- Performance style and format
- Technical rider highlights (if available)
- Past notable venues/events (if available)

# 📞 Contact & Booking
- Management/booking contact details
- Social media and streaming links
- Website and press materials

The final EPK should be comprehensive, professional, and designed to attract booking agencies and event promoters, with a fun and colorful presentation style.
"""

INTERNAL_REPORT_INTEGRATION_PROMPT = """
You are an expert music industry analyst. You will receive multiple Internal Reports from AI models. Your task is to generate a professionally formatted, publication-ready LaTeX document by following these steps:

Processing Steps:
1. Integrate Valuable Insights: Extract and incorporate useful data, insights, or recommendations from the other reports to enhance the final version
2. Eliminate Redundancies: Remove repetitive or unnecessary information to ensure clarity and conciseness
3. Finalize for Publication: Replace any placeholders, refine the language, and structure the report to be visually appealing and professionally formatted in LaTeX

Output Requirements:
• Do not wrap the content in any code blocks or markdown syntax
• Maintain a strictly formal and professional tone
• Use emojis strategically to enhance visual appeal and engagement
• Use monospace fonts for a formal, professional appearance
• Include a prominent header stating "CONFIDENTIAL" at the top of the document

LaTeX Document Structure:
\\documentclass{article}
\\usepackage{fontspec}
\\usepackage{emoji}
\\setmainfont{Noto Color Emoji}
\\begin{document}

Report Structure Requirements:

# 📈 Performance Analytics
- Detailed streaming metrics analysis across all platforms
- Month-over-month growth trends with percentage changes
- Platform-specific performance insights (e.g., Spotify, Apple Music, YouTube, TikTok)
- Comparative analysis against previous periods

# 🌍 Audience Development
- Follower growth rates across major platforms
- Engagement metrics and patterns (likes, comments, shares)
- Geographic distribution of listeners (top countries/cities)
- Platform-specific audience behavior (e.g., active hours, retention rates)

# 🎵 Release Impact Analysis
- Performance metrics for recent releases (stream counts, saves, playlist additions)
- Comparison of original tracks vs. remixes in terms of engagement and reach
- Collaboration impact on streaming numbers and audience crossover
- Effectiveness of release timing (day of the week, seasonal trends)

# 📱 Distribution & Platform Strategy
- Platform-by-platform presence analysis (gaps, strengths)
- Identification of gaps in digital distribution
- Optimization opportunities for each streaming/social platform
- Content strategy recommendations based on past performance

# 🏆 Market Position Assessment
- Genre positioning (comparisons with similar artists)
- Competitive landscape (benchmarking against industry peers)
- Growth opportunities (new platforms, untapped audiences)
- Risk factors (declining metrics, audience shifts)

# 🚀 Action Items & Recommendations
- Short-term optimization steps (quick wins for immediate impact)
- Long-term strategic initiatives (sustained growth strategies)
- Platform-specific recommendations (e.g., ad spend allocation, content tweaks)
- Investment priorities (where to allocate marketing and production resources)

The final report should be comprehensive, professional, and designed for internal decision-making, with a formal and confidential presentation style.
"""


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
        # Create cache path
        artist_name_slug = artist_data["stage_name"].replace(" ", "_")
        artist_dir = os.path.join("data", "artists", artist_name_slug, "cache")
        cache_path = os.path.join(
            artist_dir, f"{artist_name_slug}_epk_{model_name.replace('/', '_')}.txt"
        )

        # Create directory if needed
        os.makedirs(artist_dir, exist_ok=True)

        # Check cache
        if os.path.exists(cache_path):
            Logger.info(f"Using cached EPK from {cache_path}")
            with open(cache_path, "r") as f:
                return f.read()

        # Proceed with API call if not cached
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
        )
        response.raise_for_status()
        response_data = response.json()
        if not response_data.get("choices") or not response_data["choices"][0].get(
            "message"
        ):
            raise ValueError("Invalid response structure from OpenRouter API")

        # Cache the result
        with open(cache_path, "w") as f:
            f.write(response_data["choices"][0]["message"]["content"])

        return response_data["choices"][0]["message"]["content"]
    except Exception as e:
        return handle_report_error(e, model_name, artist_data, "EPK")


async def generate_internal_report(artist_data: dict, model_name: str) -> str:
    """Generate internal report using the specified model"""
    try:
        # Create cache path
        artist_name_slug = artist_data["stage_name"].replace(" ", "_")
        artist_dir = os.path.join("data", "artists", artist_name_slug, "cache")
        cache_path = os.path.join(
            artist_dir,
            f"{artist_name_slug}_internal_report_{model_name.replace('/', '_')}.txt",
        )

        # Create directory if needed
        os.makedirs(artist_dir, exist_ok=True)

        # Check cache
        if os.path.exists(cache_path):
            Logger.info(f"Using cached internal report from {cache_path}")
            with open(cache_path, "r") as f:
                return f.read()

        # Proceed with API call if not cached
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
        response_data = response.json()
        if not response_data.get("choices") or not response_data["choices"][0].get(
            "message"
        ):
            raise ValueError("Invalid response structure from OpenRouter API")

        # Cache the result
        with open(cache_path, "w") as f:
            f.write(response_data["choices"][0]["message"]["content"])

        return response_data["choices"][0]["message"]["content"]
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


async def integrate_reports(reports: dict) -> dict:
    """Integrate multiple reports into optimized versions and return as dictionary"""
    try:
        final_reports = {"EPK": None, "Internal Report": None}

        # Handle EPK reports
        if len(reports["EPK"]) == 1:
            single_epk_model = next(iter(reports["EPK"]))
            final_reports["EPK"] = reports["EPK"][single_epk_model]
        else:
            # Process EPKs
            epk_response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://audiokit.ai",
                    "X-Title": "AudioKit",
                },
                json={
                    "model": EPK_INTEGRATION_MODEL,
                    "messages": [
                        {"role": "system", "content": EPK_INTEGRATION_PROMPT},
                        {
                            "role": "user",
                            "content": json.dumps({"EPKs": reports["EPK"]}),
                        },
                    ],
                },
            )
            epk_response.raise_for_status()

            # Validate response structure with improved error handling
            try:
                # First try to decode the JSON
                try:
                    response_data = epk_response.json()
                except json.JSONDecodeError as decode_error:
                    Logger.error(f"Failed to decode JSON response: {str(decode_error)}")
                    Logger.info(
                        f"Raw response content: {epk_response.text[:500]}"
                    )  # Log first 500 chars
                    final_reports["EPK"] = (
                        "EPK integration failed: Invalid JSON response from API"
                    )
                    return final_reports

                # Then validate the structure
                if not response_data.get("choices") or not response_data["choices"][
                    0
                ].get("message"):
                    Logger.error("Invalid response structure - missing required fields")
                    Logger.info(f"Response data: {json.dumps(response_data, indent=2)}")
                    final_reports["EPK"] = (
                        "EPK integration failed: Invalid API response structure"
                    )
                    return final_reports

                # If we get here, the response is valid
                final_reports["EPK"] = response_data["choices"][0]["message"]["content"]

            except Exception as e:
                Logger.error(
                    f"Unexpected error during EPK response processing: {str(e)}"
                )
                final_reports["EPK"] = "EPK integration failed: Unexpected error"
                return final_reports

        # Handle Internal Reports
        if len(reports["Internal Report"]) == 1:
            single_internal_model = next(iter(reports["Internal Report"]))
            final_reports["Internal Report"] = reports["Internal Report"][
                single_internal_model
            ]
        else:
            # Process Internal Reports
            internal_response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://audiokit.ai",
                    "X-Title": "AudioKit",
                },
                json={
                    "model": INTERNAL_REPORT_INTEGRATION_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": INTERNAL_REPORT_INTEGRATION_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "Internal Reports": reports["Internal Report"],
                                }
                            ),
                        },
                    ],
                },
            )
            internal_response.raise_for_status()

            # Validate response structure with improved error handling
            try:
                # First try to decode the JSON
                try:
                    response_data = internal_response.json()
                except json.JSONDecodeError as decode_error:
                    Logger.error(f"Failed to decode JSON response: {str(decode_error)}")
                    Logger.info(
                        f"Raw response content: {internal_response.text[:500]}"
                    )  # Log first 500 chars
                    final_reports["Internal Report"] = (
                        "Internal Report integration failed: Invalid JSON response from API"
                    )
                    return final_reports

                # Then validate the structure
                if not response_data.get("choices") or not response_data["choices"][
                    0
                ].get("message"):
                    Logger.error("Invalid response structure - missing required fields")
                    Logger.info(f"Response data: {json.dumps(response_data, indent=2)}")
                    final_reports["Internal Report"] = (
                        "Internal Report integration failed: Invalid API response structure"
                    )
                    return final_reports

                # If we get here, the response is valid
                final_reports["Internal Report"] = response_data["choices"][0][
                    "message"
                ]["content"]

            except Exception as e:
                Logger.error(
                    f"Unexpected error during internal report response processing: {str(e)}"
                )
                final_reports["Internal Report"] = (
                    "Internal Report integration failed: Unexpected error"
                )
                return final_reports

        return final_reports

    except requests.exceptions.RequestException as e:
        Logger.error(f"API request failed: {str(e)}")
        return {
            "EPK": "EPK integration failed: API request error",
            "Internal Report": "Internal Report integration failed: API request error",
        }
    except Exception as e:
        Logger.error(f"Unexpected error during report integration: {str(e)}")
        return {
            "EPK": "EPK integration failed: Unexpected error",
            "Internal Report": "Internal Report integration failed: Unexpected error",
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

        # Integrate and optimize reports
        Logger.info("Starting report integration process")
        strategy_start = Logger.start_task("Report integration")
        integrated_reports = await integrate_reports(all_reports)
        Logger.end_task(strategy_start, "Report integration completed")
        Logger.success("Reports integrated and optimized")

        # Save reports
        Logger.info("Starting report saving process")
        save_start = Logger.start_task("Saving reports")
        artist_name_slug = artist_data["stage_name"].replace(" ", "_")

        # Create artist directory if it doesn't exist
        artist_dir = os.path.join("data", "artists", artist_name_slug)
        os.makedirs(artist_dir, exist_ok=True)
        Logger.success(f"Created artist directory at {artist_dir}")

        # Save integrated reports as LaTeX files
        Logger.info("Saving integrated reports as LaTeX files")
        if integrated_reports["EPK"]:
            epk_filename = os.path.join(
                artist_dir, f"{artist_name_slug}_integrated_epk.tex"
            )
            with open(epk_filename, "w") as f:
                f.write(integrated_reports["EPK"])
            Logger.success(f"Saved integrated EPK to {epk_filename}")

        if integrated_reports["Internal Report"]:
            internal_filename = os.path.join(
                artist_dir, f"{artist_name_slug}_integrated_internal_report.tex"
            )
            with open(internal_filename, "w") as f:
                f.write(integrated_reports["Internal Report"])
            Logger.success(f"Saved internal report to {internal_filename}")

        Logger.end_task(save_start, "Reports saved successfully")
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
