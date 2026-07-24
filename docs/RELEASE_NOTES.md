# CryptoSage v1.0.0

Release date: 2026-07-24

## Included

- FastAPI cryptocurrency intelligence API with async PostgreSQL persistence.
- JWT/refresh-token authentication and Argon2 password storage.
- CoinGecko market intelligence, Redis caching, portfolio analytics, and WebSocket updates.
- Celery worker and Beat, Prometheus/Grafana monitoring, Docker Compose, NGINX, Alembic, and GitHub Actions CI.
- 16 passing tests, 92.07% coverage, clean dependency audit, full Compose smoke test, and measured local benchmark baseline.

## Release checks

- Lint: passed.
- Tests: passed.
- Coverage: 92.07%.
- Dependency audit: no known vulnerabilities.
- Container build and full Compose startup: passed.
- API liveness/readiness and Prometheus metrics: passed.

## Known operational boundaries

- Benchmark numbers are local baseline results only.
- Production deployment still requires operator-owned TLS, backups, alerting, secret rotation, managed service credentials, and a chosen open-source license if the repository will be public.
