-- Year-over-year sales, profit and margin (window function for YoY growth)
WITH yearly AS (
    SELECT order_year,
           SUM(sales)  AS sales,
           SUM(profit) AS profit
    FROM orders GROUP BY order_year
)
SELECT
    order_year,
    ROUND(sales, 0)                              AS sales,
    ROUND(profit, 0)                             AS profit,
    ROUND(100.0 * profit / sales, 2)             AS profit_margin_pct,
    ROUND(100.0 * (sales / LAG(sales) OVER (ORDER BY order_year) - 1), 1)  AS sales_yoy_pct,
    ROUND(100.0 * (profit / LAG(profit) OVER (ORDER BY order_year) - 1), 1) AS profit_yoy_pct
FROM yearly
ORDER BY order_year;
