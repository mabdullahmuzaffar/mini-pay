SELECT 
    DATE(t.created_at) AS day,
    COUNT(t.id) AS successful_txns,
    COUNT(c.id) FILTER (WHERE c.callback_status = 'SUCCESS') AS callback_successes,
    (COUNT(t.id) - COUNT(c.id) FILTER (WHERE c.callback_status = 'SUCCESS')) AS discrepancy
FROM transactions t
LEFT JOIN callbacks c ON t.id = c.transaction_id
WHERE t.status = 'SUCCESS'
GROUP BY day
ORDER BY day ASC;
