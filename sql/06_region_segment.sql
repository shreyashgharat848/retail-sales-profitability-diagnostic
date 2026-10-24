-- Profitability by region and customer segment
SELECT
    region,
    segment,
    ROUND(SUM(sales), 0)                       AS sales,
    ROUND(SUM(profit), 0)                      AS profit,
    ROUND(100.0 * SUM(profit) / SUM(sales), 2) AS profit_margin_pct,
    ROUND(AVG(discount) * 100, 1)              AS avg_discount_pct
FROM orders
GROUP BY region, segment
ORDER BY region, segment;
