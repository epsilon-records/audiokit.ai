import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from datetime import date
import time
from datetime import datetime
import traceback
import hashlib
from config import cfg  # Directly import the configured instance


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
                        cfg.api.openrouter.base_url,
                        headers={
                            "Authorization": f"Bearer {cfg.api.openrouter.api_key}",
                            "HTTP-Referer": cfg.api.headers.referer,
                            "X-Title": cfg.api.headers.title,
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
    cache_path = cfg.get_path("cache_dir", artist_name_slug).joinpath(
        f"{artist_name_slug}_epk_{model_name.replace('/', '_')}_{input_hash}.txt"
    )

    return await LLMRequest.execute(
        model_name=model_name,
        system_prompt=cfg.prompts.epk_system,
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
    cache_path = cfg.get_path("cache_dir", artist_name_slug).joinpath(
        f"{artist_name_slug}_internal_{model_name.replace('/', '_')}_{input_hash}.txt"
    )

    return await LLMRequest.execute(
        model_name=model_name,
        system_prompt=cfg.prompts.internal_report,
        user_content=json.dumps(artist_data),
        cache_path=cache_path,
        process_name=f"Internal Report Generation ({model_name})",
    )


async def integrate_reports(reports: dict, artist_name_slug: str) -> dict:
    """Integrated reports using DRY handler"""
    try:
        final_reports = {"EPK": None, "Internal Report": None}
        cache_dir = cfg.get_path("cache_dir", artist_name_slug)

        # EPK Integration
        epk_cache_path = cache_dir.joinpath(f"{artist_name_slug}_integrated_epk.tex")
        if not os.path.exists(epk_cache_path):
            final_reports["EPK"] = await LLMRequest.execute(
                model_name=cfg.models.epk_integration,
                system_prompt=cfg.prompts.epk_integration,
                user_content=json.dumps({"EPKs": reports["EPK"]}),
                cache_path=epk_cache_path,
                process_name="EPK Integration",
                retry_on_stream_error=False,
            )

        # Internal Report Integration
        internal_cache_path = cache_dir.joinpath(
            f"{artist_name_slug}_integrated_internal.tex"
        )
        if not os.path.exists(internal_cache_path):
            final_reports["Internal Report"] = await LLMRequest.execute(
                model_name=cfg.models.internal_report_integration,
                system_prompt=cfg.prompts.internal_report_integration,
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
    cache_path = cfg.get_path("cache_dir", artist_name_slug).joinpath(
        f"{artist_name_slug}_{report_type.replace(' ', '_')}_beautified_{content_hash}.tex"
    )

    return await LLMRequest.execute(
        model_name=cfg.models.beautification,
        system_prompt=cfg.prompts.beautification,
        user_content=content,
        cache_path=cache_path,
        process_name=f"{report_type} Beautification",
        retry_on_stream_error=False,
    )


async def generate_booking_emails(artist_data: dict, artist_name_slug: str) -> list:
    """Generate booking emails using DRY handler"""
    content_hash = hashlib.sha256(json.dumps(artist_data).encode()).hexdigest()[:12]
    cache_path = cfg.get_path("cache_dir", artist_name_slug).joinpath(
        f"{artist_name_slug}_booking_emails_{content_hash}.txt"
    )

    return await LLMRequest.execute(
        model_name=cfg.models.booking,
        system_prompt=cfg.prompts.booking_research.format(
            artist_data=json.dumps(artist_data)
        ),
        user_content=cfg.prompts.booking_research.format(
            artist_data=json.dumps(artist_data)
        ),
        cache_path=cache_path,
        process_name="Booking Email Research",
    )


async def generate_reports(artist_data: dict):
    """Generate all reports using available models"""
    reports = {"EPK": {}, "Internal Report": {}}
    total_models = len(cfg.models.ai_models)
    total_steps = (
        len(reports) * total_models
    )  # Calculate based on number of report types and models
    current_step = 0

    Logger.info(
        f"Starting report generation for {artist_data.get('stage_name', 'Unknown Artist')}"
    )
    Logger.info(f"Total models to process: {total_models}")
    Logger.info(f"Total steps to complete: {total_steps}")

    for model_name in cfg.models.ai_models:
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
        email_dir = cfg.get_path("email_dir", artist_name_slug)
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

            filename = email_dir.joinpath(
                f"{artist_name_slug}_booking_{agency_name}_{idx}.txt"
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
        connection = psycopg2.connect(cfg.db_url, cursor_factory=RealDictCursor)
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
