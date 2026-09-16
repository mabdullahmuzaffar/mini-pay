-- STEP 1: Baseline plan (run first, before creating the index)
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, transaction_ref, customer_id, amount, status, created_at, completed_at
FROM transactions
WHERE transaction_ref = 'TXN00012345';

-- STEP 2: Create the index
CREATE INDEX IF NOT EXISTS idx_transactions_transaction_ref
    ON transactions (transaction_ref);

ANALYZE transactions;

-- STEP 3: Same query, now with the index
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, transaction_ref, customer_id, amount, status, created_at, completed_at
FROM transactions
WHERE transaction_ref = 'TXN00012345';
