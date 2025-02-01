import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import httpx

from .logger import Logger
from .models import ArtistData
from config import cfg


class Report(BaseModel):
    content: str
    model_name: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ReportCollection(BaseModel):
    epk: Dict[str, Report] = Field(default_factory=dict)
    internal: Dict[str, Report] = Field(default_factory=dict)


class OpenRouterClient:
    """Simple client for OpenRouter API"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.base_url = f"{cfg.api.openrouter.base_url}/api/v1"
        self.client = httpx.AsyncClient(
            headers={
                "HTTP-Referer": cfg.api.headers.referer,
                "X-Title": cfg.api.headers.title,
                "Authorization": f"Bearer {cfg.api.openrouter.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30.0,
        )

    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """Send a chat completion request to OpenRouter"""
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": messages,
                },
            )
            response.raise_for_status()
            result = response.json()

            # Extract content from response
            content = (
                result.get("choices", [{}])[0].get("message", {}).get("content", "")
            )

            if not content:
                raise ValueError("Empty response from OpenRouter API")

            return content

        except httpx.HTTPError as e:
            error_msg = str(e)
            Logger.error(f"OpenRouter API request failed: {error_msg}")

            if "429" in error_msg:
                raise ValueError("Rate limit exceeded - please wait before retrying")
            if "402" in error_msg:
                raise ValueError(
                    "Insufficient credits - please check your OpenRouter balance"
                )
            if "401" in error_msg:
                raise ValueError("Authentication failed - check your API key")

            raise ValueError(f"HTTP error: {error_msg}")

        except Exception as e:
            Logger.error(f"Unexpected error in chat completion: {str(e)}")
            raise ValueError(f"Failed to get completion: {str(e)}")

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class BaseGenerator:
    """Base class for text generators"""

    def __init__(self, model_name: str, system_prompt: str, name: str):
        self.client = OpenRouterClient(model_name)
        self.system_prompt = system_prompt
        self.name = name

    async def generate(self, data: Any) -> str:
        """Generate text based on input data"""
        try:
            Logger.info(
                f"Sending request to {self.name} with model {self.client.model_name}"
            )

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self._format_data(data)},
            ]

            result = await self.client.chat_completion(messages)

            # Validate response
            if len(result.strip()) < 50:
                Logger.error(f"Suspiciously short response from {self.name}: {result}")
                raise ValueError(f"Response too short from {self.name}")

            Logger.info(f"Got response from {self.name}: {result[:100]}...")
            return result

        except Exception as e:
            Logger.error(f"Failed to generate with {self.name}: {str(e)}")
            raise ValueError(f"Generation failed with {self.name}: {str(e)}")

        finally:
            await self.client.close()

    def _format_data(self, data: Any) -> str:
        """Format input data for the prompt - override in subclasses"""
        # Handle Pydantic models by converting to dict first
        if hasattr(data, "model_dump"):
            data = data.model_dump()
        elif hasattr(data, "dict"):
            data = data.dict()
        return json.dumps(data, indent=2)


class EPKGenerator(BaseGenerator):
    """Generates Electronic Press Kits"""

    def __init__(self, model_name: str):
        super().__init__(
            model_name=model_name,
            system_prompt=cfg.prompts.epk_system,
            name="EPK Generator",
        )


class InternalReportGenerator(BaseGenerator):
    """Generates Internal Reports"""

    def __init__(self, model_name: str):
        super().__init__(
            model_name=model_name,
            system_prompt=cfg.prompts.internal_report,
            name="Internal Report Generator",
        )


class BookingEmailGenerator(BaseGenerator):
    """Generates Booking Emails"""

    def __init__(self):
        super().__init__(
            model_name=cfg.models.booking,
            system_prompt=cfg.prompts.booking_research,
            name="Booking Email Generator",
        )


class ReportIntegrator(BaseGenerator):
    """Integrates multiple reports"""

    def __init__(self, model_name: str = None):
        super().__init__(
            model_name=model_name or cfg.models.epk_integration,
            system_prompt=cfg.prompts.epk_integration,
            name="Report Integration",
        )

    def _format_data(self, data: Dict[str, List[str]]) -> str:
        return json.dumps({"reports": data}, indent=2)


class ReportBeautifier(BaseGenerator):
    """Beautifies reports"""

    def __init__(self):
        super().__init__(
            model_name=cfg.models.beautification,
            system_prompt=cfg.prompts.beautification,
            name="Report Beautification",
        )


# Cache Management
def get_cache_path(
    artist_name_slug: str, report_type: str, model_name: str, content_hash: str
) -> str:
    """Generate standardized cache path"""
    filename = f"{artist_name_slug}_{report_type}_{model_name.replace('/', '_')}_{content_hash}.txt"
    return os.path.join(cfg.get_path("cache_dir", artist_name_slug), filename)


def generate_content_hash(data: Dict[str, Any]) -> str:
    """Generate stable hash for caching"""

    def normalize(obj):
        if isinstance(obj, dict):
            return {k: normalize(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [normalize(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        else:
            return str(obj)

    normalized = normalize(data)
    serialized = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()[:12]


# Main Functions
async def generate_reports(artist_data: dict) -> ReportCollection:
    """Generate all reports using available models"""
    artist = ArtistData(**artist_data)
    reports = ReportCollection()
    total_models = len(cfg.models.ai_models)

    Logger.info(f"Starting report generation for {artist.stage_name}")
    Logger.info(f"Total models to process: {total_models}")

    for model_name in cfg.models.ai_models:
        Logger.info(f"Processing model {model_name}")

        # Generate EPK
        epk_generator = EPKGenerator(model_name=model_name)
        epk_start = Logger.start_task(f"EPK generation with {model_name}")
        epk_result = await epk_generator.generate(artist)
        Logger.end_task(epk_start, f"Completed EPK generation with {model_name}")
        reports.epk[model_name] = Report(content=epk_result, model_name=model_name)

        # Generate Internal Report
        internal_generator = InternalReportGenerator(model_name=model_name)
        internal_start = Logger.start_task(
            f"Internal report generation with {model_name}"
        )
        internal_result = await internal_generator.generate(artist)
        Logger.end_task(
            internal_start, f"Completed internal report generation with {model_name}"
        )
        reports.internal[model_name] = Report(
            content=internal_result, model_name=model_name
        )

    Logger.success(f"All report generation completed for {artist.stage_name}")
    return reports


async def generate_booking_emails(artist_data: dict, artist_name_slug: str) -> str:
    """Generate booking emails

    Args:
        artist_data: Raw artist data dictionary
        artist_name_slug: Slug for caching and file paths

    Returns:
        Generated booking email content
    """
    try:
        artist = ArtistData(**artist_data)
        generator = BookingEmailGenerator()
        result = await generator.generate(artist)
        return result
    except Exception as e:
        Logger.error(f"Failed to generate booking emails: {str(e)}")
        raise ValueError(f"Booking email generation failed: {str(e)}") from e


async def integrate_reports(
    reports: ReportCollection, artist_name_slug: str
) -> Dict[str, Optional[str]]:
    """Integrate reports"""
    try:
        integrator = ReportIntegrator()
        final_reports = {"EPK": None, "Internal Report": None}

        # EPK Integration
        if reports.epk:
            Logger.info(f"Integrating {len(reports.epk)} EPK reports")
            epk_contents = [report.content for report in reports.epk.values()]
            epk_result = await integrator.generate({"EPKs": epk_contents})
            if not epk_result:
                Logger.error("EPK integration returned empty result")
            final_reports["EPK"] = epk_result
        else:
            Logger.warning("No EPK reports to integrate")

        # Internal Report Integration
        if reports.internal:
            Logger.info(f"Integrating {len(reports.internal)} Internal reports")
            internal_contents = [report.content for report in reports.internal.values()]
            internal_result = await integrator.generate(
                {"Internal Reports": internal_contents}
            )
            if not internal_result:
                Logger.error("Internal report integration returned empty result")
            final_reports["Internal Report"] = internal_result
        else:
            Logger.warning("No Internal reports to integrate")

        # Validate results
        for report_type, content in final_reports.items():
            if not content:
                Logger.error(f"No content generated for {report_type}")
            else:
                Logger.success(f"Successfully integrated {report_type}")

        return final_reports
    except Exception as e:
        Logger.error(f"Report integration failed: {str(e)}")
        raise


async def beautify_report(content: str, report_type: str, artist_name_slug: str) -> str:
    """Beautify a report"""
    try:
        if not content:
            Logger.error(f"Cannot beautify empty {report_type} content")
            return ""

        beautifier = ReportBeautifier()
        Logger.info(f"Beautifying {report_type} for {artist_name_slug}")

        # Add LaTeX wrapper if not present
        if not content.strip().startswith("\\documentclass"):
            content = f"""\\documentclass{{article}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=2cm}}
\\begin{{document}}

{content}

\\end{{document}}"""

        result = await beautifier.generate(content)

        if not result:
            Logger.error(f"Beautification returned empty result for {report_type}")
            return content  # Return original content if beautification fails

        Logger.success(f"Successfully beautified {report_type}")
        return result

    except Exception as e:
        Logger.error(f"Failed to beautify {report_type}: {str(e)}")
        return content  # Return original content if beautification fails
