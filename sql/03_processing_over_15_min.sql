SELECT 
    id,
    transaction_ref,
    amount,
    created_at
FROM transactions
WHERE status = 'PROCESSING'
  AND NOW() - created_at > INTERVAL '15 minutes';
