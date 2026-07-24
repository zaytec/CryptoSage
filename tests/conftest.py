import asyncio
import os

os.environ.update(
    {
        "ENVIRONMENT": "test",
        "DATABASE_URL": "sqlite+aiosqlite:///./test_cryptosage.db",
        "SECRET_KEY": "test-secret-key-that-is-safely-over-thirty-two-characters",
        "REDIS_URL": "redis://localhost:6399/0",
        "APP_DEBUG": "false",
    }
)

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app


class FakeRedis:
    def __init__(self):
        self.values = {}

    async def get(self, key):
        return self.values.get(key)

    async def set(self, key, value, ex=None):
        self.values[key] = value

    async def scan_iter(self, pattern):
        prefix = pattern.removesuffix("*")
        for key in list(self.values):
            if key.startswith(prefix):
                yield key

    async def delete(self, *keys):
        for key in keys:
            self.values.pop(key, None)
        return len(keys)

    async def ping(self):
        return True

    async def aclose(self):
        return None


class FakeMarketClient:
    async def markets(self, currency="usd", per_page=50):
        return [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "current_price": 60000,
                "market_cap_rank": 1,
            }
        ][:per_page]

    async def trending(self):
        return [{"item": {"id": "bitcoin"}}]

    async def market_chart(self, coin_id, currency, days):
        return {"prices": [[1, 60000]], "coin_id": coin_id, "days": days}

    async def close(self):
        return None


@pytest.fixture
def client():
    async def reset_database():
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

    asyncio.run(reset_database())
    with TestClient(app) as test_client:
        app.state.cache.redis = FakeRedis()
        app.state.market_client = FakeMarketClient()
        yield test_client
