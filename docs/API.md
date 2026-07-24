# API Reference

Interactive OpenAPI documentation is served at `/docs`; the OpenAPI document is at `/openapi.json`.

## Authentication

All protected endpoints require `Authorization: Bearer <access_token>`.

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register user with email and 12+ character password. |
| POST | `/api/v1/auth/token` | Obtain access and refresh tokens. |
| POST | `/api/v1/auth/refresh` | Rotate credentials using a refresh token. |
| GET | `/api/v1/auth/me` | Fetch current user. |

## Market intelligence

| Method | Path | Cache TTL |
|---|---|---:|
| GET | `/api/v1/market/coins?currency=usd&limit=50` | 60s |
| GET | `/api/v1/market/trending` | 180s |
| GET | `/api/v1/market/coins/{coin_id}/history?currency=usd&days=30` | 600s |
| GET | `/api/v1/market/cache-statistics` | n/a |

## Portfolios

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/portfolios` | Create a user-owned portfolio. |
| GET | `/api/v1/portfolios` | List user portfolios. |
| POST | `/api/v1/portfolios/{id}/transactions` | Add `buy` or `sell` transaction. |
| GET | `/api/v1/portfolios/{id}/analytics` | Return holdings, market value, cost basis, and unrealized P&L. |

## Operations

`GET /health/live` verifies process liveness. `GET /health/ready` checks PostgreSQL and Redis. `GET /metrics` exposes Prometheus metrics.

## WebSocket

Connect to `ws://<host>/ws/market/{currency}`. The server sends `market.update` messages. Send `ping` to receive `{ "type": "pong" }`.
