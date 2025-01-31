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
You are an expert in electronic music industry marketing. Your task is to create a visually stunning and professional Electronic Press Kit (EPK) from the provided JSON data.

The EPK should be tailored to attract booking agencies and event promoters and must be formatted in rich text for maximum visual impact.

Report Requirements:
	1.	Professional Formatting: Use clear section headings, subheadings, and bullet points for readability
	2.	Aesthetic Design: Create a polished and visually appealing layout with proper spacing and alignment
	3.	Compelling Content: Highlight key selling points, artist branding, and achievements to captivate promoters
	4.	Visual Enhancements: Use emojis sparingly to enhance key points (1-2 per section max)

Output Instructions:
	• Return ONLY the content itself - do not wrap it in any code blocks or markdown syntax
	• Ensure the document is engaging, professional, and well-structured
	• Use markdown-like formatting for headings (#, ##, ###) and lists
	• Maintain a professional tone while being approachable
	• Do not include any backticks, code block markers, or other syntax wrappers
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
You are a music industry analytics expert. Using the provided JSON data, generate a comprehensive and visually appealing internal artist report in rich text format.

Report Requirements:
	1.	Professional Formatting: Use clear section headings, subheadings, and bullet points for readability
	2.	Aesthetic Design: Create a polished and visually appealing layout with proper spacing and alignment
	3.	Compelling Content: Highlight key selling points, artist branding, and achievements
	4.	Visual Enhancements: Use emojis sparingly to enhance key points (1-2 per section max)

Output Instructions:
	• Return ONLY the content itself - do not wrap it in any code blocks or markdown syntax
	• Ensure the report is structured for clarity, professionalism, and maximum readability
	• Use markdown-like formatting for headings (#, ##, ###) and lists
	• Maintain a professional tone while being approachable
	• Do not include any backticks, code block markers, or other syntax wrappers
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
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o-2024-11-20",
    "mistralai/mistral-large-2411",
]


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
        # Create cache key and filename
        artist_name_slug = artist_data["stage_name"].replace(" ", "_")
        cache_key = f"{artist_name_slug}_epk_{model_name.replace('/', '_')}.md"

        # Check cache
        if os.path.exists(cache_key):
            Logger.info(f"Using cached EPK from {cache_key}")
            with open(cache_key, "r") as f:
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
        with open(cache_key, "w") as f:
            f.write(response_data["choices"][0]["message"]["content"])

        return response_data["choices"][0]["message"]["content"]
    except Exception as e:
        return handle_report_error(e, model_name, artist_data, "EPK")


async def generate_internal_report(artist_data: dict, model_name: str) -> str:
    """Generate internal report using the specified model"""
    try:
        # Create cache key and filename
        artist_name_slug = artist_data["stage_name"].replace(" ", "_")
        cache_key = (
            f"{artist_name_slug}_internal_report_{model_name.replace('/', '_')}.md"
        )

        # Check cache
        if os.path.exists(cache_key):
            Logger.info(f"Using cached internal report from {cache_key}")
            with open(cache_key, "r") as f:
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
        with open(cache_key, "w") as f:
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
    """Integrate multiple reports into optimized versions"""
    try:
        # If there's only one report for each type, return them directly
        if len(reports["EPK"]) == 1 and len(reports["Internal Report"]) == 1:
            single_epk_model = next(iter(reports["EPK"]))
            single_internal_model = next(iter(reports["Internal Report"]))
            return {
                "selected_models": {
                    "EPK": single_epk_model,
                    "Internal Report": single_internal_model,
                },
                "final_epk_report": reports["EPK"][single_epk_model],
                "final_internal_analysis": reports["Internal Report"][
                    single_internal_model
                ],
                "budget_allocation": {},
            }

        # Process EPKs separately
        epk_system_prompt = (
            "You are an expert music marketing strategist and professional document designer. Create a complete LaTeX document that will compile into a polished PDF EPK. Follow these guidelines:\n\n"
            "Document Style Requirements:\n"
            "• Compact and dense layout - maximize content per page\n"
            "• Professional music industry aesthetic - not academic\n"
            "• Use modern, fun fonts that reflect the artist's brand\n"
            "• Minimal whitespace - content should flow efficiently\n"
            "• Two-column layout for optimal space utilization\n\n"
            "Document Structure:\n"
            "\\section*{Artist Overview}\n"
            "- Craft a compelling one-paragraph pitch\n"
            "- Highlight unique selling points and artistic vision\n"
            "- Include genre focus and key achievements\n\n"
            "\\section*{Performance Metrics}\n"
            "- Present streaming numbers and growth trends\n"
            "- Social media engagement highlights\n"
            "- Geographic popularity insights\n\n"
            "\\section*{Recent Releases}\n"
            "- Showcase featured tracks from past 12 months\n"
            "- Highlight notable remixes and collaborations\n"
            "- Mention significant playlist inclusions\n\n"
            "\\section*{Stage Presence}\n"
            "- Describe performance style and format\n"
            "- Include technical rider highlights\n"
            "- Mention past notable venues/events\n\n"
            "\\section*{Contact Information}\n"
            "- Provide management/booking contacts\n"
            "- Include social media and streaming links\n"
            "- Add website and press material links\n\n"
            "Formatting Requirements:\n"
            "1. Begin with \\documentclass[twocolumn]{article}\n"
            "2. Use \\usepackage{geometry} with narrow margins\n"
            "3. Include \\usepackage{graphicx} for images\n"
            "4. Use modern fonts: \\usepackage{fontspec} with 'Fira Sans' or similar\n"
            "5. Apply consistent section formatting with \\usepackage{titlesec}\n"
            "6. Use compact lists with \\usepackage{enumitem}\n"
            "7. Include proper LaTeX document structure\n\n"
            "Output Instructions:\n"
            "• Return ONLY the complete LaTeX document\n"
            "• Do not wrap the content in any code blocks or markdown syntax\n"
            "• Use a two-column layout for compact presentation\n"
            "• Include all necessary packages and preamble\n"
            "• Ensure proper document structure\n"
            "• Make it ready for direct PDF compilation\n"
            "• Do not include any explanatory text or comments\n"
            "• Do not add any section about the document itself\n"
            "• The output must be a complete, standalone LaTeX file\n"
            "• Keep the document to 1-2 pages maximum"
        )

        epk_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://audiokit.ai",
                "X-Title": "AudioKit",
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": epk_system_prompt},
                    {"role": "user", "content": json.dumps({"EPKs": reports["EPK"]})},
                ],
                "response_format": {"type": "json_object"},
            },
        )
        epk_response.raise_for_status()
        integrated_epk = epk_response.json()["choices"][0]["message"]["content"]

        # Process Internal Reports separately
        internal_system_prompt = (
            "You are an expert music industry analyst. You will receive multiple Internal Reports from AI models. Your task is to generate a professionally formatted, publication-ready rich text document by following these steps:\n\n"
            "Processing Steps:\n"
            "1. Select the Best Report: Choose the most comprehensive and high-quality version.\n"
            "2. Integrate Valuable Insights: Extract and incorporate useful data, insights, or recommendations from the other reports to enhance the final version.\n"
            "3. Eliminate Redundancies: Remove repetitive or unnecessary information to ensure clarity and conciseness.\n"
            "4. Finalize for Publication: Replace any placeholders, refine the language, and structure the report to be visually appealing and professionally formatted in rich text.\n\n"
            "Output Requirements:\n"
            "• Return only the final rich text document, fully formatted and ready for display.\n"
            "• Do not wrap the content in any code blocks or markdown syntax\n"
            "• Ensure the report is aesthetically polished, clear, and well-structured, using professional typography, section headings, bullet points, and lists.\n"
            "• Where applicable, include emojis sparingly to enhance key points.\n\n"
            "The final report should be comprehensive, professional, and designed for internal decision-making."
        )

        internal_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://audiokit.ai",
                "X-Title": "AudioKit",
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": internal_system_prompt},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {"Internal Reports": reports["Internal Report"]}
                        ),
                    },
                ],
                "response_format": {"type": "json_object"},
            },
        )
        internal_response.raise_for_status()
        integrated_internal = internal_response.json()["choices"][0]["message"][
            "content"
        ]

        return {
            "selected_models": {
                "EPK": "Integrated Version",
                "Internal Report": "Integrated Version",
            },
            "final_epk_report": integrated_epk,
            "final_internal_analysis": integrated_internal,
            "budget_allocation": {},
        }

    except Exception as e:
        Logger.warning(f"Failed to integrate reports: {str(e)}")
        return {
            "selected_models": {"EPK": "None", "Internal Report": "None"},
            "final_epk_report": f"EPK integration failed: {str(e)}",
            "final_internal_analysis": f"Internal Report integration failed: {str(e)}",
            "integrated_report": f"Report integration failed: {str(e)}",
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

        # Save integrated reports as rich text files
        Logger.info("Saving integrated reports as rich text files")
        if "final_epk_report" in integrated_reports:
            epk_filename = f"{artist_name_slug}_integrated_epk.tex"
            with open(epk_filename, "w") as f:
                f.write(integrated_reports["final_epk_report"])
            Logger.success(f"Saved integrated EPK to {epk_filename}")

        if "final_internal_analysis" in integrated_reports:
            internal_filename = f"{artist_name_slug}_integrated_internal_report.tex"
            with open(internal_filename, "w") as f:
                f.write(integrated_reports["final_internal_analysis"])
            Logger.success(f"Saved integrated internal report to {internal_filename}")

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
