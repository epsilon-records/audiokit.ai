import aioredis
from structlog import get_logger


logger = get_logger()


class DeduplicationQueue:
    def __init__(self, redis_url: str, ttl: int = 3600):
        self.redis_url = redis_url
        self.ttl = ttl  # Time-to-live in seconds
        self.redis = None

    async def connect(self):
        """Connect to Redis."""
        self.redis = await aioredis.from_url(
            self.redis_url,
            decode_responses=True,
        )
        logger.info("✅ Connected to Redis deduplication queue")

    async def is_processed(self, node_id: str) -> bool:
        """Check if a node has been recently processed."""
        if not self.redis:
            raise RuntimeError("Redis connection not established")
        return await self.redis.exists(node_id)

    async def mark_processed(self, node_id: str):
        """Mark a node as processed."""
        if not self.redis:
            raise RuntimeError("Redis connection not established")
        await self.redis.set(node_id, "1", ex=self.ttl)
        logger.debug("Marked node as processed", node_id=node_id)

    async def close(self):
        """Close the Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("✅ Closed Redis deduplication queue")
