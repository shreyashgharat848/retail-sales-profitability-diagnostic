-- Ten products that destroy the most profit
SELECT
    product_name,
    sub_category,
    COUNT(*)                     AS order_lines,
    ROUND(SUM(sales), 0)         AS sales,
    ROUND(SUM(profit), 0)        AS profit,
    ROUND(AVG(discount) * 100, 1) AS avg_discount_pct
FROM orders
GROUP BY product_name, sub_category
ORDER BY profit ASC
LIMIT 10;
