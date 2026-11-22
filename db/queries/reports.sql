-- Get all active customers over 25 years old who have made at least one order. Show the number of orders
SELECT u.first_name, u.second_name, c.date_of_birth, COUNT(o.id) AS orders_count
FROM users u
JOIN customers c ON u.id = c.user_id
LEFT JOIN orders o ON o.customer_id = c.id
WHERE u.is_active = true AND c.date_of_birth <= (CURRENT_DATE - INTERVAL '25 years')
GROUP BY u.id, u.first_name, u.second_name, c.date_of_birth
HAVING COUNT(o.id) > 0
ORDER BY COUNT(o.id);


-- Find all vehicles of a specific model with a price above the average price for that model
SELECT v.vin, v.price
FROM vehicles v
WHERE v.model_id = '2bb5382f-462d-42ac-8fb9-f223d0261941' AND v.price > (SELECT AVG(v.price) FROM vehicles v WHERE v.model_id = '2bb5382f-462d-42ac-8fb9-f223d0261941')
ORDER BY v.price DESC;


-- List all dealerships with the number of active vehicles (models that are currently in production)
SELECT d.name, (SELECT COUNT(*) FROM vehicles v JOIN models m ON v.model_id = m.id WHERE m.is_in_production = true) AS active_vehicles_count
FROM dealerships d;


-- Show the number of orders and the average vehicle price for each model and dealership
SELECT
    m.name AS model_name,
    d.name AS dealership_name,
    COUNT(o.id) AS total_orders,
    AVG(v.price) AS avg_price
FROM models m
JOIN vehicles v ON v.model_id = m.id
JOIN orders o ON o.vehicle_id = v.id
JOIN dealerships d ON d.id = v.dealership_id
GROUP BY m.id, m.name, d.id, d.name
ORDER BY avg_price DESC;


-- Find all models whose average price of active vehicles (is_active = true) is higher than the average price across all models. Show the average price and vehicle count
SELECT
    m.id AS model_id,
    m.name AS model_name,
    ROUND(AVG(v.price), 2) AS avg_model_price,
    COUNT(v.id) AS vehicles_count
FROM models m
JOIN vehicles v ON m.id = v.model_id
WHERE v.is_active = true
GROUP BY m.id, m.name
HAVING AVG(v.price) > (SELECT AVG(price) FROM vehicles WHERE is_active = true);


-- Get a list of dealerships and the number of unique models for each, including dealerships without vehicles
SELECT
    d.id,
    d.name,
    COUNT(DISTINCT v.model_id) AS unique_models
FROM dealerships d
LEFT JOIN vehicles v ON v.dealership_id = d.id
GROUP BY d.id, d.name
ORDER BY unique_models DESC;


-- Get a list of dealerships with the total value of all active vehicles and rank them
SELECT DISTINCT
    d.id AS dealership_id,
    d.name,
    SUM(v.price) OVER (PARTITION BY d.id) AS total_value
FROM dealerships d
LEFT JOIN vehicles v ON v.dealership_id = d.id AND v.is_active = true
ORDER BY total_value DESC NULLS LAST;


-- Evaluate dealership performance based on the number of orders using CASE
SELECT
    d.id,
    d.name AS dealership_name,
    c.name AS city_name,
    COUNT(o.id) AS total_orders,
    CASE
        WHEN COUNT(o.id) = 0 THEN 'No sales'
        WHEN COUNT(o.id) < 10 THEN 'Low performance'
        WHEN COUNT(o.id) BETWEEN 10 AND 50 THEN 'Medium performance'
        ELSE 'High performance'
    END AS performance_category
FROM dealerships d
LEFT JOIN cities c ON c.id = d.city_id
LEFT JOIN orders o ON o.dealership_id = d.id
GROUP BY d.id, d.name, c.name
ORDER BY total_orders DESC;


-- Show customers and their place in the ranking by the number of orders
SELECT
  u.first_name,
  u.second_name,
  COUNT(o.id) AS orders_count,
  RANK() OVER (ORDER BY COUNT(o.id) DESC) AS rank_by_orders
FROM users u
JOIN customers c ON u.id = c.user_id
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY u.id, u.first_name, u.second_name
HAVING COUNT(o.id) > 0
ORDER BY orders_count DESC;


-- Get a list of customers who have had test drives
SELECT
  u.first_name,
  u.second_name,
  u.email
FROM users u
JOIN customers c ON u.id = c.user_id
WHERE EXISTS (
  SELECT 1
  FROM test_drive_requests t
  WHERE t.customer_id = c.id
)
ORDER BY u.first_name;
