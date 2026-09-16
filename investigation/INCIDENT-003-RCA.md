# INCIDENT-003 — Transaction Search Latency Degrades Under Scale

**Priority:** P2  
**Status:** Resolved  
**Date:** 2026-09-16  

## Summary
The transaction reference search tracking dashboard encountered non-linear latency drops proportional to database row generation scale. The root cause was an unoptimized database layout lacking a B-Tree index key on `transactions.transaction_ref`, leading to heavy full-table scans.

## Diagnostic Action Chain
1. **Endpoint Telemetry:** Captured HTTP total turnaround intervals to confirm application slowness.
2. **Database Engine Profiling:** Executed `EXPLAIN (ANALYZE, BUFFERS)` to look at query evaluation metrics, finding a complete sequential table scan reading 50,000 data nodes.
3. **Index Tracking Audits:** Ran diagnostics against the system tables catalog (`pg_indexes`) to verify that no target lookup structures existed for the column.

## Operational Root Cause
The core `schema.sql` file was delivered with intentionally sparse index properties. While `transaction_ref` was configured as the most heavily hit analytical parameter, it scaled at a degraded algorithmic performance curve of **$O(N)$**. 

## Mitigation Infrastructure Action
```sql
CREATE INDEX IF NOT EXISTS idx_transactions_transaction_ref 
    ON transactions (transaction_ref);
ANALYZE transactions;
```

## Long-Term Structural Preventions
* Implement automated logging trackers (`pg_stat_statements`) to monitor slow queries early.
* Set system alerts to trigger whenever sequential scans occur against tables containing over 10,000 active nodes.
* Enforce realistic volume performance test cases in Continuous Integration (CI) pipes using fully seeded staging files instead of testing purely blank databases.
