-- For the loss-making sub-categories: is the loss caused by heavily discounted lines?
WITH loss_subcats AS (
    SELECT sub_category FROM orders GROUP BY sub_category HAVING SUM(profit) < 0
)
SELECT
    o.sub_category,
    CASE WHEN o.discount > 0.20 THEN 'over 20% discount' ELSE 'up to 20% discount' END AS discount_group,
    COUNT(*)                 AS order_lines,
    ROUND(SUM(o.sales), 0)   AS sales,
    ROUND(SUM(o.profit), 0)  AS profit
FROM orders o
JOIN loss_subcats l ON l.sub_category = o.sub_category
GROUP BY o.sub_category, discount_group
ORDER BY o.sub_category, discount_group;
