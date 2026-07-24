# CryptoSage

CryptoSage is a production-minded cryptocurrency analytics API built with FastAPI, async SQLAlchemy, PostgreSQL, Redis, Celery, WebSockets, Prometheus, and Docker.

## Run locally

Copy the sample configuration and replace `SECRET_KEY` before using this outside local development.

```bash
cp .env.example .env
docker compose up --build
```

The API is available at `http://localhost:8000/docs`; Prometheus at `:9090`; and Grafana at `:3000`.

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

The test suite covers authentication, caching, persistence, and health/metrics. For capacity testing, use a staging environment with representative CoinGecko API limits and execute 100, 500, and 1000-request scenarios with k6 or Locust; track p95 latency, error rate, throughput, and cache hit rate from `/metrics`.
