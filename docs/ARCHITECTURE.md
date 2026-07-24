# Architecture

CryptoSage is a containerized, async Python service with clear integration boundaries.

```text
Client → NGINX → FastAPI → JWT / rate limit → PostgreSQL
                              ├──────────────→ Redis cache
                              ├──────────────→ CoinGecko
                              └──────────────→ WebSocket clients

Celery worker + Beat → Redis broker → cache maintenance
Prometheus → FastAPI /metrics → Grafana
```

FastAPI owns HTTP and WebSocket delivery. SQLAlchemy async sessions provide PostgreSQL persistence. Redis serves as both the market-data cache and Celery broker/backend. The CoinGecko adapter is deliberately narrow and timeout-bound. Prometheus observes the HTTP service; Grafana queries Prometheus.

The data model centers on `users`, `portfolios`, and `transactions`; auxiliary tables retain predictions, analytics snapshots, cache statistics, and API logs. Alembic owns schema migration.

Security boundaries are environment-driven configuration, Argon2 password hashes, signed short-lived JWT access tokens, refresh tokens, request validation, CORS allowlists, and per-client rate limiting.
