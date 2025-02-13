import asyncio

from aiocache import caches
from audiokit_mcp_server.config import settings
from audiokit_mcp_server.services.api_service import APIService


async def main():
    # Initialize Redis cache
    caches.set_config(
        {
            "default": {
                "cache": "aiocache.RedisCache",
                "endpoint": settings.redis_url.split("://")[1].split(":")[0],
                "port": int(settings.redis_url.split(":")[-1].split("/")[0]),
                "db": int(settings.redis_url.split("/")[-1]),
                "timeout": settings.redis_timeout,
                "serializer": {
                    "class": "aiocache.serializers.JsonSerializer",
                },
            },
        }
    )

    # Initialize API service
    api_service = APIService(settings)

    # Test artist ingestion
    artist_name = "Kanye West"
    try:
        result = await api_service.ingest_soundcharts_api(artist_name)
        print(f"Ingestion result: {result}")
    except Exception as e:
        print(f"Error ingesting artist: {e}")


if __name__ == "__main__":
    asyncio.run(main())
