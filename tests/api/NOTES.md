# API Test Suite Notes

## Run Command
```bash
pytest tests/api -v
```
Runs in-process cleanly against local SQLite isolation. No external database services required.

## Strategic Error Boundaries (4xx vs 5xx)
* **4xx Codes (Client Side Errors):** Handled for missing assets (404), unauthenticated header elements (401), or malformed parameters (422). These match intended system tracking behaviors and do not imply core engine down-times.
* **5xx Codes (Infrastructure Failures):** Prevented from exposing internal database exceptions or stack traces to callers using global exception filters. 
* **INCIDENT-001 Resolution:** A missing record query path previously allowed Python to execute attribute lookups on `None` objects, throwing an internal 500 server crash. We deployed an explicit object existence check, returning a managed 404 error and adding `test_get_unknown_payment_returns_404` as an immutable regression guard.

## Core Ledger Idempotency Logic
The `POST /api/payments` endpoint asserts validation against incoming `transaction_ref` strings. If a client retries a transaction request due to an upstream proxy network timeout, the application layer intercepts the collision and safely returns the existing transaction entry accompanied by an idempotent **`200 OK`** response status, eliminating double charging risks.
