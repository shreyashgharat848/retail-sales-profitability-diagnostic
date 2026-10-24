-- Headline KPIs for the whole dataset
SELECT
    COUNT(*)                                   AS order_lines,
    COUNT(DISTINCT order_id)                   AS orders,
    COUNT(DISTINCT customer_id)                AS customers,
    ROUND(SUM(sales), 0)                       AS total_sales,
    ROUND(SUM(profit), 0)                      AS total_profit,
    ROUND(100.0 * SUM(profit) / SUM(sales), 2) AS profit_margin_pct,
    ROUND(AVG(discount) * 100, 2)              AS avg_discount_pct,
    SUM(is_loss_line)                          AS loss_making_lines,
    ROUND(100.0 * SUM(is_loss_line) / COUNT(*), 1) AS loss_line_pct
FROM orders;
