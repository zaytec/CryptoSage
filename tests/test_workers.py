from app.workers import tasks


class Cache:
    async def invalidate_prefix(self, prefix):
        assert prefix == "market:"
        return 3

    async def statistics(self):
        return {"hits": 4, "misses": 1}

    async def close(self):
        return None


def test_worker_tasks_run_cache_maintenance(monkeypatch):
    monkeypatch.setattr(tasks, "CacheService", Cache)
    assert tasks.invalidate_market_cache() == 3
    assert tasks.record_cache_statistics() == {"hits": 4, "misses": 1}
