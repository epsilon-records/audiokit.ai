import asyncio

from audiokit_mcp_server.config import settings
from audiokit_mcp_server.services.api_service import APIService
from audiokit_mcp_server.utils.redis import setup_redis_cache


async def main():
    # Initialize Redis cache
    setup_redis_cache(settings.redis_url, settings.redis_timeout)

    # Initialize API service
    api_service = APIService(settings)
    await api_service.startup()  # Explicitly call startup

    # Test artist ingestion
    artist_name = "Kanye West"
    try:
        result = await api_service.ingest_soundcharts_api(artist_name)
        print(f"Ingestion result: {result}")
    except Exception as e:
        print(f"Error ingesting artist: {e}")


if __name__ == "__main__":
    asyncio.run(main())
