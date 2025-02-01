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
import hashlib

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
    "deepseek/deepseek-r1",
    "anthropic/claude-3.5-sonnet",
    "openai/o1-mini",
]

# Constants for report integration
EPK_INTEGRATION_MODEL = "deepseek/deepseek-r1"
INTERNAL_REPORT_INTEGRATION_MODEL = "deepseek/deepseek-r1"

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

# Add this with other constants
BEAUTIFICATION_MODEL = "deepseek/deepseek-r1"
BEAUTIFICATION_PROMPT = """
You are a professional document formatting expert. Improve the visual presentation and formatting of this LaTeX document while maintaining all content:

Formatting Requirements:
1. Apply consistent spacing and alignment
2. Ensure proper section hierarchy with clear headings
3. Add professional document elements (header/footer, page numbers)
4. Implement color schemes using xcolor package
5. Add subtle decorative elements (e.g., horizontal rules, tasteful icons)
6. Fix any LaTeX syntax issues
7. Maintain original content structure
8. Ensure mobile-friendly formatting
9. Add responsive design elements
10. Optimize for PDF export

Do NOT:
- Alter or remove any content
- Change section order
- Modify any factual information

Output ONLY the improved LaTeX code with no additional commentary or markdown formatting.
"""

# Add new constants near other prompts
BOOKING_RESEARCH_PROMPT = """
You are an expert music industry researcher. Using all available artist data, create 5 targeted booking agency recommendations and draft professional cold emails.

Artist Data:
{artist_data}

Requirements:
1. Research 5 booking agencies that specialize in the artist's genre and location
2. For each agency:
   - Include actual verified email address
   - List 3 specific reasons why they're a good match
3. Write complete cold emails with:
   - Professional subject line
   - Personalized introduction
   - Concise pitch (3-5 sentences)
   - Clear call-to-action
   - Proper email signature

Email Format:
To: agency@email.com
Subject: [Catchy Professional Subject]

[Personalized Body]

Best,
Nate Houk
Artist Manager @ AudioKit
"""

# Add this with other constants
BOOKING_MODEL = "openai/o1-mini"


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

    @staticmethod
    def stream_log(message: str):
        """Stream partial responses with timestamp"""
        print(
            f"🧠 [STREAM] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}",
            end="\r",
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


class LLMRequest:
    @staticmethod
    async def execute(
        model_name: str,
        system_prompt: str,
        user_content: str,
        cache_path: str,
        process_name: str,
        retry_on_stream_error: bool = True,
    ) -> str:
        """Generic LLM request handler with streaming and caching"""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)

            # Check cache first
            if os.path.exists(cache_path):
                Logger.info(f"Using cached response from {cache_path}")
                with open(cache_path, "r") as f:
                    return f.read()

            retry_count = 0
            max_retries = 2 if retry_on_stream_error else 1
            final_content = ""

            while retry_count < max_retries:
                try:
                    stream = retry_count == 0  # First try with streaming
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
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_content},
                            ],
                            "stream": stream,
                        },
                        stream=stream,
                    )
                    response.raise_for_status()

                    final_content = await LLMRequest._handle_response(
                        response, process_name, model_name
                    )
                    break

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 400 and "stream" in str(e).lower():
                        Logger.warning(
                            f"Model {model_name} doesn't support streaming - retrying without"
                        )
                        retry_count += 1
                        continue
                    raise

            # Cache the result
            with open(cache_path, "w") as f:
                f.write(final_content)

            return final_content

        except Exception as e:
            Logger.error(f"LLM request failed: {str(e)}")
            raise

    @staticmethod
    async def _handle_response(response, process_name: str, model_name: str) -> str:
        """Handle both streaming and non-streaming responses"""
        full_response = []
        buffer = ""

        try:
            if response.headers.get("content-type") == "text/event-stream":
                Logger.info(f"Processing streaming response for {process_name}")
                for chunk in response.iter_lines():
                    if chunk:
                        decoded = chunk.decode().replace("data: ", "")
                        if decoded == "[DONE]":
                            break
                        try:
                            data = json.loads(decoded)
                            if "content" in data["choices"][0]["delta"]:
                                token = data["choices"][0]["delta"]["content"]
                                buffer += token
                                if token in ("\n", ".", ":", ","):
                                    Logger.stream_log(
                                        f"{process_name}: {buffer.strip()}"
                                    )
                                    full_response.append(buffer)
                                    buffer = ""
                        except json.JSONDecodeError:
                            continue
            else:
                Logger.warning(f"Processing non-streaming response for {process_name}")
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                full_response.append(content)
                Logger.stream_log(f"{process_name}: Completed non-streaming response")

            if buffer:
                full_response.append(buffer)

            return "".join(full_response)

        except Exception as e:
            Logger.error(f"Response handling failed: {str(e)}")
            raise


async def generate_epk(artist_data: dict, model_name: str) -> str:
    """Generate EPK using DRY handler"""
    sanitized_data = sanitize_artist_data(artist_data.copy())
    input_hash = hashlib.sha256(
        json.dumps(sanitized_data, sort_keys=True).encode()
    ).hexdigest()[:12]
    artist_name_slug = sanitized_data["stage_name"].replace(" ", "-").lower()
    cache_path = os.path.join(
        "data",
        "artists",
        artist_name_slug,
        "cache",
        f"{artist_name_slug}_epk_{model_name.replace('/', '_')}_{input_hash}.txt",
    )

    return await LLMRequest.execute(
        model_name=model_name,
        system_prompt=EPK_SYSTEM_PROMPT,
        user_content=json.dumps(artist_data),
        cache_path=cache_path,
        process_name=f"EPK Generation ({model_name})",
    )


async def generate_internal_report(artist_data: dict, model_name: str) -> str:
    """Generate internal report using DRY handler"""
    sanitized_data = sanitize_artist_data(artist_data.copy())
    input_hash = hashlib.sha256(
        json.dumps(sanitized_data, sort_keys=True).encode()
    ).hexdigest()[:12]
    artist_name_slug = sanitized_data["stage_name"].replace(" ", "-").lower()
    cache_path = os.path.join(
        "data",
        "artists",
        artist_name_slug,
        "cache",
        f"{artist_name_slug}_internal_{model_name.replace('/', '_')}_{input_hash}.txt",
    )

    return await LLMRequest.execute(
        model_name=model_name,
        system_prompt=INTERNAL_REPORT_PROMPT,
        user_content=json.dumps(artist_data),
        cache_path=cache_path,
        process_name=f"Internal Report Generation ({model_name})",
    )


async def integrate_reports(reports: dict, artist_name_slug: str) -> dict:
    """Integrated reports using DRY handler"""
    try:
        final_reports = {"EPK": None, "Internal Report": None}
        cache_dir = os.path.join("data", "artists", artist_name_slug, "cache")

        # EPK Integration
        epk_cache_path = os.path.join(
            cache_dir, f"{artist_name_slug}_integrated_epk.tex"
        )
        if not os.path.exists(epk_cache_path):
            final_reports["EPK"] = await LLMRequest.execute(
                model_name=EPK_INTEGRATION_MODEL,
                system_prompt=EPK_INTEGRATION_PROMPT,
                user_content=json.dumps({"EPKs": reports["EPK"]}),
                cache_path=epk_cache_path,
                process_name="EPK Integration",
                retry_on_stream_error=False,
            )

        # Internal Report Integration
        internal_cache_path = os.path.join(
            cache_dir, f"{artist_name_slug}_integrated_internal.tex"
        )
        if not os.path.exists(internal_cache_path):
            final_reports["Internal Report"] = await LLMRequest.execute(
                model_name=INTERNAL_REPORT_INTEGRATION_MODEL,
                system_prompt=INTERNAL_REPORT_INTEGRATION_PROMPT,
                user_content=json.dumps(
                    {"Internal Reports": reports["Internal Report"]}
                ),
                cache_path=internal_cache_path,
                process_name="Internal Report Integration",
                retry_on_stream_error=False,
            )

        return final_reports
    except Exception as e:
        Logger.error(f"Report integration failed: {str(e)}")
        return {"EPK": "Integration failed", "Internal Report": "Integration failed"}


async def beautify_report(content: str, report_type: str, artist_name_slug: str) -> str:
    """Beautify report using DRY handler"""
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
    cache_path = os.path.join(
        "data",
        "artists",
        artist_name_slug,
        "cache",
        f"{artist_name_slug}_{report_type.replace(' ', '_')}_beautified_{content_hash}.tex",
    )

    return await LLMRequest.execute(
        model_name=BEAUTIFICATION_MODEL,
        system_prompt=BEAUTIFICATION_PROMPT,
        user_content=content,
        cache_path=cache_path,
        process_name=f"{report_type} Beautification",
        retry_on_stream_error=False,
    )


async def generate_booking_emails(artist_data: dict, artist_name_slug: str) -> list:
    """Generate booking emails using DRY handler"""
    content_hash = hashlib.sha256(json.dumps(artist_data).encode()).hexdigest()[:12]
    cache_path = os.path.join(
        "data",
        "artists",
        artist_name_slug,
        "cache",
        f"{artist_name_slug}_booking_emails_{content_hash}.txt",
    )

    return await LLMRequest.execute(
        model_name=BOOKING_MODEL,
        system_prompt="You are a music industry professional...",
        user_content=BOOKING_RESEARCH_PROMPT.format(
            artist_data=json.dumps(artist_data)
        ),
        cache_path=cache_path,
        process_name="Booking Email Research",
    )


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


async def save_emails_to_file(content: str, artist_name_slug: str):
    """Save formatted emails to individual files"""
    try:
        email_dir = os.path.join("data", "artists", artist_name_slug, "emails")
        os.makedirs(email_dir, exist_ok=True)

        # Split emails by agency
        emails = content.split("\n\n")  # Assuming double newline separates emails
        for idx, email in enumerate(emails, 1):
            if not email.strip():
                continue

            # Extract agency name from email
            agency_name = "unknown_agency"
            if "To:" in email:
                email_part = email.split("To:")[1].split("\n")[0].strip()
                agency_name = (
                    email_part.split("@")[0].replace(".", "_").replace("-", "_")
                )

            filename = os.path.join(
                email_dir, f"{artist_name_slug}_booking_{agency_name}_{idx}.txt"
            )

            with open(filename, "w") as f:
                f.write(email)

        Logger.success(f"Saved {len(emails)} emails to {email_dir}")
        return True
    except Exception as e:
        Logger.error(f"Failed to save emails: {str(e)}")
        return False


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

        # Save reports (update filenames to reflect beautification)
        Logger.info("Starting report saving process")
        save_start = Logger.start_task("Saving reports")
        artist_dir = os.path.join("data", "artists", artist_name_slug)
        cache_dir = os.path.join(artist_dir, "cache")

        # Save beautified reports to cache
        Logger.info("Saving beautified reports to cache")
        os.makedirs(cache_dir, exist_ok=True)

        if integrated_reports["EPK"]:
            epk_filename = os.path.join(
                cache_dir, f"{artist_name_slug}_integrated_epk_beautified.tex"
            )
            with open(epk_filename, "w") as f:
                f.write(integrated_reports["EPK"])
            Logger.success(f"Saved beautified EPK to cache: {epk_filename}")

        if integrated_reports["Internal Report"]:
            internal_filename = os.path.join(
                cache_dir,
                f"{artist_name_slug}_integrated_internal_report_beautified.tex",
            )
            with open(internal_filename, "w") as f:
                f.write(integrated_reports["Internal Report"])
            Logger.success(
                f"Saved beautified internal report to cache: {internal_filename}"
            )

        Logger.end_task(save_start, "Reports saved successfully")

        # NEW: Generate booking emails
        Logger.info("Starting booking email research")
        email_start = Logger.start_task("Booking email generation")
        emails_content = await generate_booking_emails(artist_data, artist_name_slug)
        await save_emails_to_file(emails_content, artist_name_slug)
        Logger.end_task(email_start, "Booking emails generated and saved")

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
            artist_name_slug = artist_data["stage_name"].replace(" ", "-").lower()
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
