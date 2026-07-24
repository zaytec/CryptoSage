import asyncio

from app.core.cache import CacheService
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.invalidate_market_cache")
def invalidate_market_cache() -> int:
    async def work() -> int:
        cache = CacheService()
        try:
            return await cache.invalidate_prefix("market:")
        finally:
            await cache.close()

    return asyncio.run(work())


@celery_app.task(name="app.workers.tasks.record_cache_statistics")
def record_cache_statistics() -> dict[str, object]:
    async def work() -> dict[str, object]:
        cache = CacheService()
        try:
            return await cache.statistics()
        finally:
            await cache.close()

    return asyncio.run(work())
