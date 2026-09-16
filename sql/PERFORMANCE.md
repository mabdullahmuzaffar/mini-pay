# SQL Performance Analysis (INCIDENT-003)

## The Problem
`transactions.transaction_ref` had no database index configured (schema.sql omitted this deliberately). Every time a user searched for a reference tag, the engine had to perform a full sequential table scan across all 50,000 rows. This backed the UI search dashboard and the main payments endpoint—the hottest read path in the architecture.

## Before — Sequential Scan
```text
 Seq Scan on transactions  (cost=0.00..1241.00 rows=1 width=60) (actual time=1.459..5.095 rows=1 loops=1)
   Filter: ((transaction_ref)::text = 'TXN00012345'::text)
   Rows Removed by Filter: 49999
   Buffers: shared hit=616
 Planning:
   Buffers: shared hit=78
 Planning Time: 0.330 ms
 Execution Time: 5.160 ms
```
- **Plan Node:** `Seq Scan on transactions`
- **Rows Examined:** 50,000
- **Rows Returned:** 1
- **Execution Time:** 5.160 ms

## The Fix
```sql
CREATE INDEX idx_transactions_transaction_ref ON transactions (transaction_ref);
ANALYZE transactions;
```
*Note: The `ANALYZE` command updates the internal database query statistics planner immediately. In a live enterprise infrastructure system, `CREATE INDEX CONCURRENTLY` should be utilized instead to avoid hard-locking application table write tasks.*

## After — Index Scan
```text
 Index Scan using idx_transactions_transaction_ref on transactions  (cost=0.29..8.31 rows=1 width=60) (actual time=0.073..0.075 rows=1 loops=1)
   Index Cond: ((transaction_ref)::text = 'TXN00012345'::text)
   Buffers: shared hit=1 read=2
 Planning:
   Buffers: shared hit=37 read=1
 Planning Time: 1.166 ms
 Execution Time: 0.133 ms
```
- **Plan Node:** `Index Scan using idx_transactions_transaction_ref`
- **Rows Examined:** 1
- **Execution Time:** 0.133 ms

## Performance Metrics Summary

| Metric | Before Optimization | After Optimization |
| :--- | :--- | :--- |
| **Engine Execution Plan** | Seq Scan (Full Table Scan) | Index Scan (B-Tree Match) |
| **Data Rows Examined** | ~50,000 rows | 1 row |
| **Database Query Time** | 5.160 ms | 0.133 ms |
| **Buffer Pages Read** | 616 pages | 3 pages |
