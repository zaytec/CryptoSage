import json
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any, TypeVar

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings

T = TypeVar("T")


class CacheService:
    def __init__(self, redis_client: Redis | None = None) -> None:
        self.redis = redis_client or Redis.from_url(get_settings().redis_url, decode_responses=True)
        self._hits = 0
        self._misses = 0

    async def get_or_set(
        self, key: str, ttl_seconds: int, factory: Callable[[], Awaitable[T]]
    ) -> T:
        try:
            cached = await self.redis.get(key)
            if cached is not None:
                self._hits += 1
                return json.loads(cached)
            self._misses += 1
            value = await factory()
            await self.redis.set(key, json.dumps(value, default=str), ex=ttl_seconds)
            return value
        except RedisError:
            self._misses += 1
            return await factory()

    async def invalidate_prefix(self, prefix: str) -> int:
        try:
            keys = [key async for key in self.redis.scan_iter(f"{prefix}*")]
            return await self.redis.delete(*keys) if keys else 0
        except RedisError:
            return 0

    async def statistics(self) -> dict[str, Any]:
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 4) if total else 0.0,
            "observed_at": datetime.now(UTC).isoformat(),
        }

    async def close(self) -> None:
        await self.redis.aclose()
