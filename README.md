# MiniPay — Paysys Labs L2 Support Engineer Assessment

**Candidate:** Muhammad Abdullah Muzaffar
**Position:** Implementation & L2 Support Engineer
**Repository:** FILL_IN_AFTER_PUSH

## Quick start

    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements-dev.txt
    pytest tests/api -v

    docker compose up --build -d
    # UI  http://localhost:8080
    # API http://localhost:8081/health

## What is here

| Area | Location |
|---|---|
| REST API | app/ |
| SQL reports | sql/ |
| Support tool | python/support_tool.py |
| API tests (16) | tests/api/ |
| Browser tests (6) | tests/ui/ |
| Kubernetes | kubernetes/ |
| Incident RCAs | investigation/ |
| Linux evidence | evidence/ |

## Completed

- Docker Compose and Kubernetes deployment
- 7 SQL reports on 50k row dataset
- Index improvement with EXPLAIN before/after (INCIDENT-003)
- Python support tool with --transaction, --health, --json
- 16 API tests, 6 Playwright browser tests
- INCIDENT-001: 500 on missing ID, introduced and fixed in git history
- INCIDENT-002: 4 defects in starter manifest found and fixed
- INCIDENT-003: seq scan 50k rows indexed, 5ms to 0.13ms
- Linux evidence and health-check script

## Limitations

- Shared API key, not per-client identity
- Payments always succeed, no real processor
- No unique constraint on transaction_ref (schema not modified)
- Single database instance, no pagination or metrics
