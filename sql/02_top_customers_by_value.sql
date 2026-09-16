SELECT 
    c.customer_ref,
    c.name,
    COUNT(t.id) AS successful_count,
    ROUND(SUM(t.amount), 2) AS total_value
FROM customers c
JOIN transactions t ON c.id = t.customer_id
WHERE t.status = 'SUCCESS'
GROUP BY c.customer_ref, c.name
ORDER BY total_value DESC
LIMIT 10;
