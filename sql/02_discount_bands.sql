-- Core diagnostic: how does profit margin change as discount increases?
SELECT
    discount_band,
    COUNT(*)                                   AS order_lines,
    ROUND(SUM(sales), 0)                       AS sales,
    ROUND(SUM(profit), 0)                      AS profit,
    ROUND(100.0 * SUM(profit) / SUM(sales), 2) AS profit_margin_pct,
    ROUND(100.0 * SUM(is_loss_line) / COUNT(*), 1) AS loss_line_pct
FROM orders
GROUP BY discount_band
ORDER BY CASE discount_band
             WHEN '0% (none)' THEN 1 WHEN '0-20%' THEN 2
             WHEN '20-40%'   THEN 3 ELSE 4 END;
