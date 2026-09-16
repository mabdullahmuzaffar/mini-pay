SELECT 
    transaction_ref,
    COUNT(*) AS count
FROM transactions
GROUP BY transaction_ref
HAVING COUNT(*) > 1
ORDER BY count DESC, transaction_ref ASC;
