SELECT 
    DATE(created_at) AS day,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'SUCCESS') AS successful,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'SUCCESS') / COUNT(*), 2) AS success_rate_pct
FROM transactions
GROUP BY day
ORDER BY day ASC;
