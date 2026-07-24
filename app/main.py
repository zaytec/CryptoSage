import asyncio
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.api import auth, market, portfolios, system
from app.core.cache import CacheService
from app.core.config import get_settings
from app.core.database import SessionLocal, create_schema, engine
from app.models import ApiLog
from app.services.coingecko import CoinGeckoClient
from app.services.websocket import ConnectionManager

settings = get_settings()
limiter = Limiter(
    key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.environment != "production":
        await create_schema()
    app.state.cache = CacheService()
    app.state.market_client = CoinGeckoClient(str(settings.coingecko_base_url))
    app.state.connections = ConnectionManager()
    app.state.session_factory = SessionLocal
    yield
    await app.state.market_client.close()
    await app.state.cache.close()
    await engine.dispose()


app = FastAPI(title="CryptoSage", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded, lambda _request, _exc: JSONResponse({"detail": "Rate limit exceeded"}, 429)
)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def request_timing(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started) * 1000)
    response.headers["X-Request-Duration-Ms"] = str(duration_ms)
    if request.url.path != "/metrics":
        try:
            async with SessionLocal() as session:
                session.add(
                    ApiLog(
                        method=request.method,
                        path=request.url.path,
                        status_code=response.status_code,
                        duration_ms=duration_ms,
                    )
                )
                await session.commit()
        except Exception:
            # Observability must never make a successful request fail.
            pass
    return response


app.include_router(system.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(market.router, prefix="/api/v1")
app.include_router(portfolios.router, prefix="/api/v1")
Instrumentator(excluded_handlers=["/metrics"]).instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)


@app.websocket("/ws/market/{currency}")
async def market_stream(websocket: WebSocket, currency: str) -> None:
    channel = f"market:{currency.lower()}"
    manager: ConnectionManager = app.state.connections
    await manager.connect(websocket, channel)
    try:
        while True:
            markets = await app.state.market_client.markets(currency, 10)
            await websocket.send_json(
                {"type": "market.update", "at": datetime.now(UTC).isoformat(), "data": markets}
            )
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if message.lower() == "ping":
                    await websocket.send_json({"type": "pong"})
            except TimeoutError:
                continue
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket, channel)
