import asyncio

from audiokit_mcp_server.config import settings
from audiokit_mcp_server.services.api_service import APIService


async def main():
    # Initialize the API service
    api_service = APIService(settings)

    # Test with a real artist
    artist_name = "Kanye West"  # Replace with the artist you want to test
    print(f"Ingesting data for artist: {artist_name}")

    try:
        result = await api_service.ingest_soundcharts_api(artist_name)
        print("Ingestion successful!")
        print("Result:", result)
    except Exception as e:
        print("Ingestion failed:", str(e))


if __name__ == "__main__":
    asyncio.run(main())
