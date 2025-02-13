from datetime import datetime, timedelta
from functools import wraps

from structlog import get_logger


logger = get_logger()


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.is_open():
                logger.warning("Circuit breaker is open, skipping operation")
                raise RuntimeError("Circuit breaker is open")

            try:
                result = await func(*args, **kwargs)
                self.reset()
                return result
            except Exception as e:
                self.record_failure()
                logger.error(
                    "Operation failed, incrementing failure count", error=str(e)
                )
                raise

        return wrapper

    def is_open(self) -> bool:
        if self.failure_count < self.failure_threshold:
            return False
        if datetime.utcnow() - self.last_failure_time > timedelta(
            seconds=self.recovery_timeout
        ):
            self.reset()
            return False
        return True

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

    def reset(self):
        self.failure_count = 0
        self.last_failure_time = None
