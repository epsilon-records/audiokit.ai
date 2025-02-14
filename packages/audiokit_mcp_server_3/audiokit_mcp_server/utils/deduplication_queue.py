import asyncio

import aioredis
from structlog import get_logger


logger = get_logger()


class DeduplicationQueue:
    def __init__(self, redis_url: str, ttl: int = 3600, redis_connection=None):
        self.redis_url = redis_url
        self.ttl = ttl  # Time-to-live in seconds
        self.redis = redis_connection  # Use existing connection if provided

    async def connect(self):
        """Connect to Redis if no existing connection is provided."""
        if self.redis is None:
            self.redis = await aioredis.from_url(
                self.redis_url,
                decode_responses=True,
            )
            logger.info("✅ Connected to Redis deduplication queue")

    async def is_processed(self, node_id: str) -> bool:
        """Check if a node has been processed."""
        if not self.redis:
            raise RuntimeError("Redis connection not established")
        try:
            return await asyncio.wait_for(
                self.redis.sismember("deduplication_queue", node_id),
                timeout=1.0,
            )
        except asyncio.TimeoutError:
            logger.warning("Redis operation timed out", node_id=node_id)
            return False

    async def mark_processed(self, node_id: str):
        """Mark a node as processed by adding it to the deduplication queue."""
        if not self.redis:
            raise RuntimeError("Redis connection not established")
        try:
            await asyncio.wait_for(
                self.redis.sadd("deduplication_queue", node_id),
                timeout=1.0,
            )
            # Set TTL for the entire queue
            await self.redis.expire("deduplication_queue", self.ttl)
            logger.debug("Added node to deduplication queue", node_id=node_id)
        except asyncio.TimeoutError:
            logger.warning("Redis operation timed out", node_id=node_id)

    async def close(self):
        """Close the Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("✅ Closed Redis deduplication queue")

    async def clear(self) -> None:
        """Clear all entries from the deduplication queue."""
        if not self.redis:
            raise RuntimeError("Redis connection not established")

        try:
            # Ask user for confirmation
            response = (
                input("⚠️  Clear the entire Redis database? [y/N]: ").strip().lower()
            )
            if response != "y":
                logger.info("Skipping Redis cache clearance")
                return

            await asyncio.wait_for(self.redis.flushdb(), timeout=5.0)
            logger.info("🧹 Cleared deduplication queue")
        except asyncio.TimeoutError:
            logger.warning("Redis flush operation timed out")
        except Exception as e:
            logger.error("Failed to clear Redis cache", error=str(e))
            raise
