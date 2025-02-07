import redis
from datetime import timedelta
from .config import ServerConfig

class RedisRateLimiter:
    def __init__(self, config: ServerConfig):
        self.redis = redis.Redis.from_url(config.rate_limiting.redis_url)
        self.default_limit = config.rate_limiting.default_limit
        self.limits = config.rate_limiting.limits

    async def check_limit(self, key: str, path: str) -> bool:
        limit = self.limits.get(path, self.default_limit)
        current = self.redis.incr(f"rate_limit:{key}:{path}")
        
        if current == 1:  # Set expiration on first request
            self.redis.expire(f"rate_limit:{key}:{path}", 60)
            
        return current <= limit 