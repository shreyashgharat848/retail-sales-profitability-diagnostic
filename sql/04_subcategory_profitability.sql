-- Profitability by sub-category, flagging loss-makers and the share of lines sold at >20% discount
SELECT
    category,
    sub_category,
    ROUND(SUM(sales), 0)                       AS sales,
    ROUND(SUM(profit), 0)                      AS profit,
    ROUND(100.0 * SUM(profit) / SUM(sales), 2) AS profit_margin_pct,
    ROUND(AVG(discount) * 100, 1)              AS avg_discount_pct,
    ROUND(100.0 * SUM(CASE WHEN discount > 0.20 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                               AS pct_lines_over_20_discount,
    CASE WHEN SUM(profit) < 0 THEN 'LOSS-MAKING' ELSE 'profitable' END AS status
FROM orders
GROUP BY category, sub_category
ORDER BY profit ASC;
