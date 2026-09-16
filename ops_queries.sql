-- Boxleo Mock WMS — 10 Real Operations Queries
-- Each answers a question a warehouse/ops manager would actually ask.

-- 1. Which SKUs are at or below their reorder point right now? (stockout risk)
SELECT product_name, warehouse_location, quantity, reorder_point
FROM inventory
WHERE quantity <= reorder_point
ORDER BY quantity ASC;

-- 2. How many orders are currently delayed, broken down by country?
SELECT country, COUNT(*) AS delayed_orders
FROM orders
WHERE status = 'delayed'
GROUP BY country
ORDER BY delayed_orders DESC;

-- 3. What is the on-time delivery rate overall (delivered orders only)?
SELECT
    ROUND(100.0 * SUM(CASE WHEN delivery_status = 'on_time' THEN 1 ELSE 0 END) / COUNT(*), 1) AS on_time_pct
FROM shipments
WHERE delivery_status IN ('on_time', 'late');

-- 4. On-time delivery rate BY country — this is where the hub-vs-spoke gap should show up.
SELECT o.country,
    ROUND(100.0 * SUM(CASE WHEN s.delivery_status = 'on_time' THEN 1 ELSE 0 END) / COUNT(*), 1) AS on_time_pct,
    COUNT(*) AS total_delivered
FROM shipments s
JOIN orders o ON s.order_id = o.order_id
WHERE s.delivery_status IN ('on_time', 'late')
GROUP BY o.country
ORDER BY on_time_pct ASC;

-- 5. Which merchant has generated the most revenue from delivered orders?
SELECT m.name, ROUND(SUM(o.amount), 2) AS total_revenue
FROM orders o
JOIN merchants m ON o.merchant_id = m.merchant_id
WHERE o.status = 'delivered'
GROUP BY m.name
ORDER BY total_revenue DESC;

-- 6. How many orders has each region manager's portfolio handled?
SELECT m.region_manager, COUNT(o.order_id) AS orders_handled
FROM orders o
JOIN merchants m ON o.merchant_id = m.merchant_id
GROUP BY m.region_manager
ORDER BY orders_handled DESC;

-- 7. Which warehouse has the most orders still not shipped?
SELECT warehouse_location, COUNT(*) AS not_shipped_count
FROM shipments
WHERE delivery_status = 'not_shipped'
GROUP BY warehouse_location
ORDER BY not_shipped_count DESC;

-- 8. Average order value by country.
SELECT country, ROUND(AVG(amount), 2) AS avg_order_value
FROM orders
GROUP BY country
ORDER BY avg_order_value DESC;

-- 9. Which SKUs are completely out of stock (quantity = 0)?
SELECT product_name, warehouse_location, merchant_id
FROM inventory
WHERE quantity = 0;

-- 10. Cancellation rate by merchant — a signal of merchant-side problems (bad listings, fraud, etc.)
SELECT m.name,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
    ROUND(100.0 * SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1) AS cancel_pct
FROM orders o
JOIN merchants m ON o.merchant_id = m.merchant_id
GROUP BY m.name
ORDER BY cancel_pct DESC;
