# CryptoSage

CryptoSage v1.0.0 is a cryptocurrency analytics API built with FastAPI, async SQLAlchemy, PostgreSQL, Redis, Celery, WebSockets, Prometheus, and Docker.

## Highlights

- JWT authentication with Argon2 password hashing and refresh tokens.
- Redis cache-aside strategy for market data, with cache statistics and scheduled invalidation.
- Portfolio transactions, cost basis, holdings valuation, and unrealized P&L.
- Async CoinGecko integration, WebSocket market stream, and Celery maintenance jobs.
- PostgreSQL migrations, health probes, Prometheus metrics, Grafana, NGINX, Docker Compose, and CI.

Detailed material is available in [architecture](docs/ARCHITECTURE.md), [API documentation](docs/API.md), [deployment guide](docs/DEPLOYMENT.md), [benchmark report](docs/BENCHMARKS.md), and [release notes](docs/RELEASE_NOTES.md).

## Run locally

Copy the sample configuration and replace all development secrets before using this outside local development.

```bash
cp .env.example .env
docker compose up --build
```

The API is available at `http://localhost:8000/docs`; Prometheus at `:9090`; and Grafana at `:3000`.

For production, set `ENVIRONMENT=production`, a unique `SECRET_KEY`, explicit CORS origins, and non-default PostgreSQL credentials. The application refuses to start in production with the sample JWT secret or wildcard CORS.

## Core API

- `POST /api/v1/auth/register`, `/token`, `/refresh`
- `GET /api/v1/market/coins`, `/trending`, `/coins/{coin_id}/history`
- `POST /api/v1/portfolios`; `POST /api/v1/portfolios/{id}/transactions`
- `GET /api/v1/portfolios/{id}/analytics`
- `WS /ws/market/{currency}` for live market snapshots; clients may send `ping`.

Market data is cached with endpoint-appropriate TTLs (60 seconds for prices, 180 for trending, 600 for historical data). Redis failures degrade gracefully for read endpoints, while readiness correctly reports dependency failures.

## Operations

Run schema migrations with `alembic upgrade head`. The Compose stack starts API, Celery worker/beat, PostgreSQL, Redis, Prometheus, and Grafana. Put the provided NGINX configuration in front of the API in an internet-facing deployment. Railway and AWS deployments should supply all values from `.env.example` through their secret managers, run `alembic upgrade head` as a release command, and expose `/health/live` and `/health/ready` to the platform health checks.

## Quality checks

```bash
pip install -e '.[dev]'
ruff check .
pytest
docker compose config
```

The suite covers authentication, caching, persistence, WebSockets, Celery tasks, and health/metrics. The release baseline is 16 passing tests and 92.07% coverage. Actual local benchmark results are documented in [docs/BENCHMARKS.md](docs/BENCHMARKS.md).
