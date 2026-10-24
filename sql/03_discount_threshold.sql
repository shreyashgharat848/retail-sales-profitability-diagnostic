-- Threshold test: margin at or below 20% discount vs strictly above 20%
SELECT
    CASE WHEN discount = 0     THEN 'a) no discount'
         WHEN discount <= 0.20 THEN 'b) 0-20% discount'
         WHEN discount <= 0.40 THEN 'c) 20-40% discount'
         ELSE                       'd) over 40% discount' END AS discount_group,
    COUNT(*)                                   AS order_lines,
    ROUND(100.0 * SUM(profit) / SUM(sales), 2) AS profit_margin_pct
FROM orders
GROUP BY 1
UNION ALL
SELECT 'e) ALL lines over 20% discount', COUNT(*),
       ROUND(100.0 * SUM(profit) / SUM(sales), 2)
FROM orders WHERE discount > 0.20
UNION ALL
SELECT 'f) ALL lines up to 20% discount', COUNT(*),
       ROUND(100.0 * SUM(profit) / SUM(sales), 2)
FROM orders WHERE discount <= 0.20
ORDER BY 1;
