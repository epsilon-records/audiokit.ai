import json
import os
import requests
import time
import hashlib
from .logger import Logger
from .utils import sanitize_artist_data
from config import cfg
from typing import Dict, Any
from datetime import datetime


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
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)

            if os.path.exists(cache_path):
                Logger.info(f"Using cached response from {cache_path}")
                with open(cache_path, "r") as f:
                    return f.read()

            if not cfg.api.openrouter.api_key:
                raise ValueError("OpenRouter API key is missing in configuration")

            # Use streaming for deepseek model on first attempt
            use_streaming = model_name.startswith("deepseek/deepseek-r1")

            Logger.info(
                f"{process_name}: Making request {'with' if use_streaming else 'without'} streaming"
            )

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
                    "stream": use_streaming,
                    "temperature": 0.7,
                    "max_tokens": 4000,
                },
                stream=use_streaming,
                timeout=60,
            )
            response.raise_for_status()

            if use_streaming:
                final_content = await LLMRequest._handle_response(
                    response, process_name, model_name
                )
            else:
                data = response.json()
                final_content = data["choices"][0]["message"]["content"]
                Logger.success(f"{process_name}: Received complete response")

            # Validate response content
            if not final_content or len(final_content.strip()) < 50:
                raise ValueError("Response content too short or empty")

            # For booking emails, validate completeness before caching
            if process_name.startswith("Booking"):
                if (
                    "**To:**" not in final_content
                    or "**Subject:**" not in final_content
                ):
                    Logger.warning("Incomplete email response - not caching")
                    raise ValueError("Generated email content is incomplete")

            # Cache the valid response
            with open(cache_path, "w") as f:
                f.write(final_content)
            Logger.success(f"Cached complete response to {cache_path}")
            return final_content

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                Logger.error(
                    "Authentication failed - please check your OpenRouter API key"
                )
                raise ValueError("Invalid OpenRouter API key") from e
            error_data = e.response.json() if e.response.content else {}
            error_msg = f"HTTP error {e.response.status_code}: {error_data.get('error', str(e))}"
            Logger.error(error_msg)
            raise ValueError(error_msg) from e

        except requests.exceptions.Timeout as e:
            error_msg = f"Request timeout after {60} seconds"
            Logger.error(error_msg)
            raise ValueError(error_msg) from e

        except Exception as e:
            Logger.error(f"LLM request failed: {str(e)}")
            raise

    @staticmethod
    async def _handle_response(response, process_name: str, model_name: str) -> str:
        full_response = []
        buffer = ""
        last_log_time = time.time()
        min_log_interval = 0.5

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

                                current_time = time.time()
                                if token in ("\n", ".", "!", "?") or (
                                    current_time - last_log_time >= min_log_interval
                                ):
                                    if buffer.strip():
                                        Logger.stream_log(
                                            f"{process_name}: {buffer.strip()}"
                                        )
                                        full_response.append(buffer)
                                        buffer = ""
                                    last_log_time = current_time
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
                Logger.stream_log(f"{process_name}: {buffer.strip()}")

            return "".join(full_response)

        except Exception as e:
            Logger.error(f"Response handling failed: {str(e)}")
            raise


def generate_stable_hash(data: Dict[str, Any]) -> str:
    """
    Generate a stable hash for a dictionary.
    Ensures consistent hashing by:
    1. Sorting dictionary keys
    2. Using consistent JSON serialization
    3. Handling nested dictionaries and lists
    """

    def normalize(obj):
        if isinstance(obj, dict):
            return {k: normalize(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [normalize(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        else:
            return str(obj)  # Convert other types to strings

    normalized_data = normalize(data)
    serialized = json.dumps(normalized_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()[:12]


def normalize_timestamps(data: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat(timespec="seconds")  # Round to seconds
    return data


async def generate_epk(artist_data: dict, model_name: str) -> str:
    """Generate EPK using DRY handler"""
    sanitized_data = normalize_timestamps(sanitize_artist_data(artist_data.copy()))
    input_hash = generate_stable_hash(sanitized_data)
    artist_name_slug = sanitized_data["stage_name"].replace(" ", "-").lower()
    cache_path = cfg.get_path("cache_dir", artist_name_slug).joinpath(
        f"{artist_name_slug}_epk_{model_name.replace('/', '_')}_{input_hash}.txt"
    )

    # Check if cached version exists
    if os.path.exists(cache_path):
        Logger.info(f"Using cached EPK from {cache_path}")
        with open(cache_path, "r") as f:
            return f.read()

    # If no cache exists, generate new one
    return await LLMRequest.execute(
        model_name=model_name,
        system_prompt=cfg.prompts.epk_system,
        user_content=json.dumps(artist_data),
        cache_path=cache_path,
        process_name=f"EPK Generation ({model_name})",
    )


async def generate_internal_report(artist_data: dict, model_name: str) -> str:
    """Generate internal report using DRY handler"""
    sanitized_data = normalize_timestamps(sanitize_artist_data(artist_data.copy()))
    input_hash = generate_stable_hash(sanitized_data)
    artist_name_slug = sanitized_data["stage_name"].replace(" ", "-").lower()
    cache_path = cfg.get_path("cache_dir", artist_name_slug).joinpath(
        f"{artist_name_slug}_internal_{model_name.replace('/', '_')}_{input_hash}.txt"
    )

    # Check if cached version exists
    if os.path.exists(cache_path):
        Logger.info(f"Using cached internal report from {cache_path}")
        with open(cache_path, "r") as f:
            return f.read()

    # If no cache exists, generate new one
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


async def generate_booking_emails(artist_data: dict, artist_name_slug: str) -> str:
    """Generate booking emails using DRY handler"""
    try:
        # Validate artist data has required fields
        required_fields = ["stage_name", "email", "phone"]
        for field in required_fields:
            if field not in artist_data or not artist_data[field]:
                raise ValueError(f"Missing required field: {field}")

        content_hash = hashlib.sha256(json.dumps(artist_data).encode()).hexdigest()[:12]
        cache_path = cfg.get_path("cache_dir", artist_name_slug).joinpath(
            f"{artist_name_slug}_booking_emails_{content_hash}.txt"
        )

        # Check if cached version exists and is valid
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                content = f.read()
                if "**To:**" in content and "**Subject:**" in content:
                    return content

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
    except Exception as e:
        Logger.error(f"Failed to generate booking emails: {str(e)}")
        raise ValueError(f"Booking email generation failed: {str(e)}") from e


async def generate_reports(artist_data: dict) -> dict:
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
