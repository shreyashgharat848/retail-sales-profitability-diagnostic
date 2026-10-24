-- Customer-level Recency / Frequency / Monetary base table (used by the K-Means step)
-- Recency is measured from the day after the last order in the dataset.
SELECT
    customer_id,
    customer_name,
    segment                                                       AS customer_type,
    CAST(julianday((SELECT DATE(MAX(order_date), '+1 day') FROM orders))
         - julianday(MAX(order_date)) AS INTEGER)                 AS recency_days,
    COUNT(DISTINCT order_id)                                      AS frequency,
    ROUND(SUM(sales), 2)                                          AS monetary,
    ROUND(SUM(profit), 2)                                         AS total_profit
FROM orders
GROUP BY customer_id, customer_name, segment;
