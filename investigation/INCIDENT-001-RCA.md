# INCIDENT-001 — HTTP 500 on Transaction Lookup

**Priority:** P2
**Status:** Resolved
**Date:** 2026-09-16

## Summary

Support reported intermittent HTTP 500 on transaction search. Fully
deterministic — every request for a non-existent payment ID returned 500.
Appeared intermittent because agents mixed valid and invalid references.

## Reproduction

    curl -s -w 'HTTP %{http_code}' http://localhost:8081/api/payments/99999
    HTTP 500  (buggy version)

    curl -s -w 'HTTP %{http_code}' http://localhost:8081/api/payments/1
    HTTP 200  (valid id always worked)

## Evidence from logs

    ResponseValidationError: Input should be a valid dictionary or object,
    input: None

db.query(...).first() returns None for missing records. Code returned None
to the serialiser which raised an exception converted to 500.

## Root Cause

get_payment_by_id had no None check after the query. Session.first()
returns None when no row matches. None flowed into response serialisation
and caused an unhandled exception.

A missing resource is a client error (404), not a server fault (500).

## Fix

    # Buggy: no guard
    txn = db.query(models.Transaction).filter(...).first()
    return txn

    # Fixed
    txn = db.query(models.Transaction).filter(...).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn

## Validation

    curl -s -w 'HTTP %{http_code}' http://localhost:8081/api/payments/99999
    HTTP 404

    pytest tests/api -v
    16 passed

## Git history

    git log --oneline --grep=INCIDENT-001
    Shows: bug commit then fix commit. Full cycle is reproducible.

## Prevention

1. Every db.query(...).first() must have a None check
2. test_get_unknown_payment_returns_404 is the regression guard
3. Alert on 5xx rate not individual occurrences
4. X-Request-ID on every response including 500s for log correlation
