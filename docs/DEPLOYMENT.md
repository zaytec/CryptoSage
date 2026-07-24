# Deployment Guide

## Production configuration

Create a private `.env` from `.env.example`. Set `ENVIRONMENT=production`, a unique 32+ character `SECRET_KEY`, the production `DATABASE_URL`, `REDIS_URL`, CORS origins, and PostgreSQL credentials. `.env` overrides the bundled development defaults when Compose starts.

The application rejects sample JWT secrets and wildcard CORS in production mode.

## Compose deployment

```bash
docker compose up --build -d
curl --fail http://localhost:8000/health/ready
```

The API executes `alembic upgrade head` before Uvicorn starts. Compose health-checks PostgreSQL and Redis before dependent services start. Place the supplied NGINX configuration in front of the API for TLS termination and WebSocket proxying.

## Cloud deployment

For Railway, AWS ECS, Kubernetes, or a Linux host, deploy the API, worker, and Beat as separate process/container units. Use managed PostgreSQL and Redis, inject secrets from the platform secret manager, run Alembic as a release job, and configure `/health/live` and `/health/ready` as probes.

Expose only the load balancer/NGINX publicly. Restrict PostgreSQL, Redis, Prometheus, and Grafana to private networks or authenticated operator access.

## Release verification

1. Run `ruff check .`, `pytest`, `pip-audit`, and `docker compose config --quiet`.
2. Build the image and start the complete Compose stack.
3. Confirm API readiness, worker/Beat startup, Prometheus scraping, and Grafana availability.
4. Apply platform-specific TLS, backups, secret rotation, and alerting policies before internet exposure.
