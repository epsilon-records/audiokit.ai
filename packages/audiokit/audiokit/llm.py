import json
import os
import requests
import time
import hashlib
from .logger import Logger
from .utils import sanitize_artist_data
from config import cfg


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

            retry_count = 0
            max_retries = 2 if retry_on_stream_error else 1
            final_content = ""

            while retry_count < max_retries:
                try:
                    # Only use streaming for deepseek model
                    use_streaming = (
                        model_name.startswith("deepseek/deepseek-r1")
                        and retry_count == 0
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
                        },
                        stream=use_streaming,
                    )
                    response.raise_for_status()

                    if use_streaming:
                        final_content = await LLMRequest._handle_response(
                            response, process_name, model_name
                        )
                    else:
                        # Process complete response
                        data = response.json()
                        final_content = data["choices"][0]["message"]["content"]
                        Logger.success(f"{process_name}: Received complete response")
                    break

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 401:
                        Logger.error(
                            "Authentication failed - please check your OpenRouter API key"
                        )
                        raise ValueError("Invalid OpenRouter API key") from e
                    if e.response.status_code == 400:
                        Logger.warning(
                            f"Request failed for {model_name} - retrying with different settings"
                        )
                        retry_count += 1
                        continue
                    raise

            # Only write to cache if we have a complete response
            if final_content:
                # For booking emails, validate completeness before caching
                if process_name.startswith("Booking"):
                    if (
                        "**To:**" not in final_content
                        or "**Subject:**" not in final_content
                    ):
                        Logger.warning("Incomplete email response - not caching")
                        raise ValueError("Generated email content is incomplete")

                with open(cache_path, "w") as f:
                    f.write(final_content)
                Logger.success(f"Cached complete response to {cache_path}")
            else:
                Logger.warning(f"No complete response received for {process_name}")
                raise ValueError("No complete response received from API")

            return final_content

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


async def generate_booking_emails(artist_data: dict, artist_name_slug: str) -> str:
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
