from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import httpx
import pytest

from app.models import Portfolio, Transaction
from app.services.coingecko import CoinGeckoClient
from app.services.portfolio import portfolio_analytics
from app.services.websocket import ConnectionManager


@pytest.mark.asyncio
async def test_coingecko_adapter_shapes_provider_requests():
    seen = []

    async def handler(request):
        seen.append(str(request.url))
        if request.url.path == "/search/trending":
            return httpx.Response(200, json={"coins": [{"item": {"id": "bitcoin"}}]})
        return httpx.Response(200, json=[{"id": "bitcoin", "current_price": 1}])

    client = CoinGeckoClient(
        "https://provider.test",
        httpx.AsyncClient(base_url="https://provider.test", transport=httpx.MockTransport(handler)),
    )
    assert (await client.markets())[0]["id"] == "bitcoin"
    assert (await client.trending())[0]["item"]["id"] == "bitcoin"
    await client.market_chart("bitcoin", "usd", 30)
    assert any("market_chart" in request for request in seen)
    await client.close()


class Socket:
    def __init__(self, fail=False):
        self.accepted = False
        self.messages = []
        self.fail = fail

    async def accept(self):
        self.accepted = True

    async def send_json(self, message):
        if self.fail:
            raise RuntimeError("disconnected")
        self.messages.append(message)


@pytest.mark.asyncio
async def test_websocket_manager_broadcasts_and_removes_stale_connections():
    manager = ConnectionManager()
    active, stale = Socket(), Socket(fail=True)
    await manager.connect(active, "market:usd")
    await manager.connect(stale, "market:usd")
    await manager.broadcast("market:usd", {"price": 1})
    assert active.messages == [{"price": 1}]
    assert manager.connection_count == 1
    await manager.disconnect(active, "market:usd")
    assert manager.connection_count == 0


class ScalarResult:
    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values


class PortfolioSession:
    def __init__(self, transactions):
        self.transactions = transactions

    async def scalars(self, _statement):
        return ScalarResult(self.transactions)


@pytest.mark.asyncio
async def test_portfolio_analytics_calculates_position_and_pnl():
    portfolio = Portfolio(id=uuid4(), user_id=uuid4(), name="Test", base_currency="usd")
    transaction = Transaction(
        portfolio_id=portfolio.id,
        coin_id="bitcoin",
        symbol="btc",
        transaction_type="buy",
        quantity=Decimal("2"),
        price=Decimal("100"),
        fees=Decimal("5"),
        occurred_at=datetime.now(UTC),
    )

    class Market:
        async def markets(self, _currency, per_page=250):
            return [{"id": "bitcoin", "current_price": 150}]

    result = await portfolio_analytics(PortfolioSession([transaction]), portfolio, Market())
    assert result.total_cost_basis == Decimal("205")
    assert result.total_market_value == Decimal("300")
    assert result.unrealized_pnl == Decimal("95")
