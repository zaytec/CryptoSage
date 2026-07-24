from typing import Any

import httpx


class CoinGeckoClient:
    """Small, timeout-bound adapter around the public CoinGecko API."""

    def __init__(self, base_url: str, client: httpx.AsyncClient | None = None) -> None:
        self._owns_client = client is None
        self.client = client or httpx.AsyncClient(base_url=base_url, timeout=httpx.Timeout(8.0))

    async def markets(self, currency: str = "usd", per_page: int = 50) -> list[dict[str, Any]]:
        response = await self.client.get(
            "/coins/markets",
            params={
                "vs_currency": currency,
                "order": "market_cap_desc",
                "per_page": per_page,
                "page": 1,
            },
        )
        response.raise_for_status()
        return response.json()

    async def trending(self) -> list[dict[str, Any]]:
        response = await self.client.get("/search/trending")
        response.raise_for_status()
        return response.json().get("coins", [])

    async def market_chart(self, coin_id: str, currency: str, days: int) -> dict[str, Any]:
        response = await self.client.get(
            f"/coins/{coin_id}/market_chart", params={"vs_currency": currency, "days": days}
        )
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()
