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
                ssl=False,  # Explicitly disable SSL
            )
            logger.info("✅ Connected to Redis deduplication queue")

    async def is_processed(self, node_id: str) -> bool:
        """Check if a node has been recently processed."""
        if not self.redis:
            raise RuntimeError("Redis connection not established")
        try:
            return await asyncio.wait_for(self.redis.exists(node_id), timeout=1.0)
        except asyncio.TimeoutError:
            logger.warning("Redis operation timed out", node_id=node_id)
            return False

    async def mark_processed(self, node_id: str):
        """Mark a node as processed."""
        if not self.redis:
            raise RuntimeError("Redis connection not established")
        try:
            await asyncio.wait_for(
                self.redis.set(node_id, "1", ex=self.ttl), timeout=1.0
            )
            logger.debug("Marked node as processed", node_id=node_id)
        except asyncio.TimeoutError:
            logger.warning("Redis operation timed out", node_id=node_id)

    async def close(self):
        """Close the Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("✅ Closed Redis deduplication queue")
