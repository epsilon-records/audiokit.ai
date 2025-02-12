import json
import os
from typing import Dict, List, Optional

import aiohttp
from fastapi import HTTPException

from audiokit_mcp_server.core.llm import call_llm
from audiokit_mcp_server.core.logger import logger
from audiokit_mcp_server.core.markdown import save_artist_report


class OpenRouterConfig:
    """Configuration for OpenRouter API"""

    API_KEY = os.getenv("OPENROUTER_API_KEY")
    API_BASE = "https://openrouter.ai/api/v1"
    MODEL = "openai/o1-mini"

    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {cls.API_KEY}",
            "HTTP-Referer": "https://audiokit.io",  # Replace with your domain
            "X-Title": "AudioKit Analytics",  # Your app name
        }


class SoundchartsClient:
    """Client for Soundcharts API."""

    def __init__(self):
        """Initialize client with API credentials."""
        self.base_url = (
            "https://customer.api.soundcharts.com"  # Base URL without version
        )
        self.app_id = os.getenv("SOUNDCHARTS_APP_ID")
        self.api_key = os.getenv("SOUNDCHARTS_API_KEY")

        if not self.app_id or not self.api_key:
            raise ValueError("SOUNDCHARTS_APP_ID and SOUNDCHARTS_API_KEY must be set")

        # For sandbox testing, you can use these credentials:
        if self.app_id == "soundcharts" and self.api_key == "soundcharts":
            logger.info("Using Soundcharts sandbox credentials")
            self.base_url = "https://customer.api.soundcharts.com/api/v2"

        logger.info("🎵 Initializing Soundcharts client...")
        logger.info(f"🔑 Using App ID: {self.app_id}")
        logger.info(f"🌐 Base URL: {self.base_url}")

    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "x-app-id": str(self.app_id),
            "x-api-key": str(self.api_key),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def get_artist_by_spotify_uri(self, spotify_uri: str) -> Optional[str]:
        """Get Soundcharts artist ID from Spotify URI"""
        try:
            logger.info(f"🔍 Looking up artist with Spotify URI: {spotify_uri}")

            # Use the correct endpoint from v2.9 API
            url = f"{self.base_url}/api/v2.9/artist/by-platform/spotify/{spotify_uri}"
            headers = self.get_headers()

            logger.debug("📡 Making API request:")
            logger.debug(f"   URL: {url}")
            logger.debug(f"   Headers: {json.dumps(headers, indent=2)}")

            async with aiohttp.ClientSession() as session:
                logger.debug("🌐 Sending request...")
                async with session.get(
                    url,
                    headers=headers,
                ) as response:
                    response_text = await response.text()
                    logger.debug(f"📥 Response status: {response.status}")
                    logger.debug(
                        f"📄 Response body: {json.dumps(json.loads(response_text), indent=2)}",
                    )

                    if response.status == 404:
                        logger.warning(f"❌ Artist not found: {spotify_uri}")
                        return None

                    if response.status != 200:
                        error_text = response_text
                        logger.error(f"🚨 API error ({response.status}): {error_text}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Soundcharts API error: {error_text}",
                        )

                    try:
                        data = await response.json()
                        # Get UUID from the nested object structure
                        artist_id = data.get("object", {}).get("uuid")
                        if artist_id:
                            logger.info(f"✅ Found Soundcharts artist ID: {artist_id}")
                            return artist_id
                        logger.warning("❌ No UUID found in response")
                        return None
                    except Exception as e:
                        logger.error(f"💥 Failed to parse response JSON: {e!s}")
                        logger.error(f"📄 Raw response: {response_text}")
                        raise

        except Exception as e:
            logger.error(f"💥 Request failed: {e!s}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get artist from Soundcharts: {e!s}",
            )

    async def get_artist_data(self, artist_id: str) -> Dict:
        """Get complete artist data from Soundcharts"""
        try:
            logger.info(f"📊 Fetching data for artist ID: {artist_id}")

            # Define endpoints with their specific versions
            endpoints = {
                "metadata": f"/api/v2.9/artist/{artist_id}",  # v2.9 for metadata
                "current_stats": f"/api/v2/artist/{artist_id}/current/stats",  # v2 for stats
                "audience": f"/api/v2/artist/{artist_id}/audience/spotify",  # v2 for audience
                "streaming": f"/api/v2/artist/{artist_id}/streaming/spotify/listening",  # v2 for streaming
                "social": f"/api/v2.37/artist/{artist_id}/social/spotify/followers",  # v2.37 for social
                "charts": f"/api/v2/artist/{artist_id}/charts/song/ranks/spotify",  # v2 for charts
                "playlists": f"/api/v2.20/artist/{artist_id}/playlist/current/spotify",  # v2.20 for playlists
                "albums": f"/api/v2.34/artist/{artist_id}/albums",  # v2.34 for albums
            }

            data = {}
            async with aiohttp.ClientSession() as session:
                for key, endpoint in endpoints.items():
                    try:
                        url = f"{self.base_url}{endpoint}"
                        logger.info(f"🔄 Fetching {key}:")
                        logger.debug(f"   URL: {url}")

                        async with session.get(
                            url,
                            headers=self.get_headers(),
                        ) as response:
                            response_text = await response.text()
                            if response.status != 200:
                                logger.warning(
                                    f"⚠️  Failed to get {key}: Status {response.status}",
                                )
                                logger.debug(f"   Response: {response_text}")
                                continue

                            response_data = json.loads(response_text)
                            if response_data:
                                logger.info(f"✅ Successfully fetched {key} data")
                                logger.debug(
                                    f"   Data: {json.dumps(response_data, indent=2)}",
                                )
                                data[key] = response_data
                            else:
                                logger.warning(f"⚠️  Empty response for {key}")

                    except Exception as e:
                        logger.error(f"❌ Error fetching {key}: {e!s}")
                        continue

            if not data:
                logger.warning("❌ No data found for any endpoints")
                raise HTTPException(status_code=404, detail="No data found for artist")

            logger.info(f"📊 Fetched data for {len(data)} endpoints")
            return data

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"💥 Failed to get artist data: {e!s}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get artist data: {e!s}",
            )

    async def generate_insight(
        self,
        data: Dict,
        context: List[Dict],
    ) -> str:
        """Generate insights from artist data"""
        try:
            # Get artist metadata and ID
            artist_info = data.get("metadata", {}).get("object", {})
            artist_name = artist_info.get("name", "Unknown Artist")
            artist_id = artist_info.get("uuid", "unknown")

            # Extract image URLs
            avatar_url = artist_info.get("avatar_url", "")
            image_urls = [
                url
                for url in [
                    avatar_url,
                    *[
                        link.get("url")
                        for link in artist_info.get("links", [])
                        if link.get("type") == "image"
                    ],
                ]
                if url
            ]

            # Extract releases and other key data
            releases = data.get("albums", {}).get("items", [])
            streaming_stats = data.get("streaming", {})
            social_stats = data.get("social", {})
            chart_data = data.get("charts", {})

            # Create prompt with structured format request
            prompt = f"""
Here’s a refined version of your prompt that allows for more creativity in structuring the report while ensuring all data and images are incorporated. It also emphasizes the importance of calculating derived statistics based on the provided data.

You are a senior music industry analyst, tasked with creating a high-impact Electronic Press Kit (EPK) report for an artist.

Your goal is to craft a compelling, professionally formatted markdown report that presents the artist in the most favorable light for industry professionals, media outlets, and music executives. The report should be engaging, insightful, and strategically structured to maximize its impact.

While you have full creative freedom in structuring the report, it must incorporate all provided data, images, and relevant statistics. Additionally, derive meaningful insights from the data, such as trends, averages, growth rates, or comparisons, to strengthen the narrative. The report should feel polished, data-driven, and visually appealing while maintaining readability.

Provided Data
	•	Artist Overview (name, number of releases, chart history)
	•	Streaming & Social Media Performance (detailed stats on platforms)
	•	Releases (list of past releases with dates)
	•	Artist Images (URLs for visuals)
	•	Full Artist Data (JSON dataset for deeper analysis)

Expectations:
	•	All data and images must be seamlessly integrated into the report.
	•	Derived statistics must be calculated where applicable to provide additional insights.
	•	Formatting should be clean, industry-standard, and visually effective.
	•	The structure should be optimized for impact, but is not bound to predefined sections.

Now, generate the EPK report in markdown.
---
Artist Overview
- **Artist Name:** {artist_name}
- **Total Releases:** {len(releases)}
- **Chart Performance:** {json.dumps(chart_data, indent=2) if chart_data else "No chart data"}

Streaming Stats
{json.dumps(streaming_stats, indent=2) if streaming_stats else "No streaming data"}

Social Media Stats
{json.dumps(social_stats, indent=2) if social_stats else "No social media data"}

Releases
{chr(10).join([f"- {release.get('name', 'Untitled')} ({release.get('release_date', 'Unknown date')})" for release in releases]) if releases else "No release data available"}

Artist Images
{chr(10).join([f"![Artist Image]({url})" for url in image_urls]) if image_urls else "No images available"}

Full Artist Data
```json
{json.dumps(data, indent=2)}
```
"""

            # Call OpenRouter LLM with formal prompt
            response = await call_llm(prompt)

            # Save as HTML and get URL
            report_url = save_artist_report(artist_id, artist_name, response)

            return response, report_url

        except Exception as e:
            logger.error(f"Failed to generate insight: {e!s}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate insight: {e!s}",
            )
