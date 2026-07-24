# Benchmark Report

## Method

Executed locally on 2026-07-24 against the Compose API using ApacheBench and the liveness endpoint:

```bash
ab -n <requests> -c <concurrency> -q http://127.0.0.1:8000/health/live
```

PostgreSQL and Redis were running in Docker. Rate limiting was raised to 10,000 requests/minute for this isolated benchmark only. The endpoint exercises FastAPI middleware, Prometheus instrumentation, and API-log persistence, but does not call CoinGecko; results are a local service baseline, not an internet-facing capacity claim.

| Requests | Concurrency | Failures | Throughput | Mean request time | p95 | p99 |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 10 | 0 | 204.43 req/s | 48.917 ms | 225 ms | 231 ms |
| 500 | 25 | 0 | 352.23 req/s | 70.977 ms | 242 ms | 266 ms |
| 1,000 | 50 | 0 | 481.67 req/s | 103.807 ms | 265 ms | 406 ms |

## Interpretation

All three executed scenarios completed with zero failed requests. Re-run this suite in a staging environment with production-sized resources, TLS, representative authentication traffic, and CoinGecko quota behavior before establishing service-level objectives.
