SELECT 
    DATE(created_at) AS day,
    status,
    COUNT(*) AS count,
    ROUND(SUM(amount), 2) AS total_value
FROM transactions
GROUP BY day, status
ORDER BY day ASC, status ASC;
