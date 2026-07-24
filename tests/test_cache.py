import pytest

from app.core.cache import CacheService
from tests.conftest import FakeRedis


@pytest.mark.asyncio
async def test_cache_returns_cached_value_and_tracks_hit():
    cache = CacheService(FakeRedis())
    calls = 0

    async def factory():
        nonlocal calls
        calls += 1
        return {"price": 42}

    assert await cache.get_or_set("market:btc", 60, factory) == {"price": 42}
    assert await cache.get_or_set("market:btc", 60, factory) == {"price": 42}
    assert calls == 1
    assert (await cache.statistics())["hit_rate"] == 0.5


@pytest.mark.asyncio
async def test_cache_invalidates_prefix():
    cache = CacheService(FakeRedis())
    await cache.redis.set("market:coins", "[]")
    await cache.redis.set("portfolio:one", "{}")
    assert await cache.invalidate_prefix("market:") == 1
    assert await cache.redis.get("market:coins") is None
    assert await cache.redis.get("portfolio:one") == "{}"
