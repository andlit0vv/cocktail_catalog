import asyncio
from datetime import datetime, timedelta
from app.config import settings


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._requests: dict[int, list[datetime]] = {}
        self._lock = asyncio.Lock()

    async def check(self, user_id: int) -> bool:
        async with self._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=60)
            timestamps = self._requests.get(user_id, [])
            timestamps = [t for t in timestamps if t > window_start]
            if len(timestamps) >= settings.assistant_rate_limit_per_min:
                self._requests[user_id] = timestamps
                return False
            timestamps.append(now)
            self._requests[user_id] = timestamps
            return True


rate_limiter = InMemoryRateLimiter()
