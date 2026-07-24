from fastapi import APIRouter, HTTPException, Query, Request
from httpx import HTTPError

from app.services.coingecko import CoinGeckoClient

router = APIRouter(prefix="/market", tags=["market intelligence"])


async def cached_market(request: Request, key: str, ttl: int, factory):
    try:
        return await request.app.state.cache.get_or_set(key, ttl, factory)
    except HTTPError as exc:
        raise HTTPException(status_code=503, detail="Market data provider unavailable") from exc


@router.get("/coins")
async def coins(
    request: Request,
    currency: str = Query("usd", pattern="^[a-z]{3}$"),
    limit: int = Query(50, ge=1, le=250),
):
    client: CoinGeckoClient = request.app.state.market_client
    return await cached_market(
        request, f"market:coins:{currency}:{limit}", 60, lambda: client.markets(currency, limit)
    )


@router.get("/trending")
async def trending(request: Request):
    client: CoinGeckoClient = request.app.state.market_client
    return await cached_market(request, "market:trending", 180, client.trending)


@router.get("/coins/{coin_id}/history")
async def history(
    coin_id: str,
    request: Request,
    currency: str = Query("usd", pattern="^[a-z]{3}$"),
    days: int = Query(30, ge=1, le=3650),
):
    client: CoinGeckoClient = request.app.state.market_client
    return await cached_market(
        request,
        f"market:history:{coin_id}:{currency}:{days}",
        600,
        lambda: client.market_chart(coin_id, currency, days),
    )


@router.get("/cache-statistics")
async def cache_statistics(request: Request):
    return await request.app.state.cache.statistics()
