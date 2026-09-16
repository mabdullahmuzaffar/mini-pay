# Architecture

## Overview

    Browser -> nginx :80 -> FastAPI :8080 -> PostgreSQL :5432

nginx serves the static UI and proxies /api/ and /health to the API.
Same images run in Docker Compose and Kubernetes.

## Technology choices

FastAPI: Pydantic validation and free OpenAPI docs built in.
PostgreSQL 16: Matches supplied schema, EXPLAIN ANALYZE for INCIDENT-003.
SQLAlchemy ORM: Parameter binding prevents SQL injection.
nginx proxy: Same-origin requests, no CORS needed.
kind: Runs on existing Docker daemon, no registry needed.
StatefulSet for Postgres: Stable identity and volumeClaimTemplate.
Playwright Python: Auto-waiting, one language across the repo.

## Endpoints

GET  /health                     - 503 if DB unreachable
POST /api/customers              - X-API-Key required, 409 on duplicate
GET  /api/customers/{id}/payments - 404 if unknown customer
POST /api/payments               - X-API-Key, idempotent on transaction_ref
GET  /api/payments/{id}          - 404 if missing (INCIDENT-001 fix)
GET  /api/transactions?ref=      - search by reference

## Key decisions

Idempotency: POST /api/payments returns 200 for replay, 201 for new record.
Payment clients retry on timeout. Without this a timed-out successful
request becomes a double charge on retry.

4xx vs 5xx: 404 = resource missing (client error).
500 = unhandled fault (our problem). INCIDENT-001 was this boundary wrong.

Request correlation: Every response carries X-Request-ID including 500s.

## Limitations

- Shared API key, no per-client identity or rotation
- Payments always succeed, no real processor integration
- No unique constraint on transaction_ref
- Single database, no replication or backup
- No pagination, metrics or tracing
