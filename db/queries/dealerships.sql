-- Get paginated dealerships with city data
SELECT d.*, c.name as city_name, c.country
FROM dealerships d
LEFT JOIN cities c ON c.id = d.city_id
OFFSET 20 LIMIT 20;


-- Count total dealerships
SELECT COUNT(*) FROM dealerships;


-- Count active dealerships
SELECT COUNT(*) FROM dealerships WHERE is_active = true;


-- Get dealership by ID with city data
SELECT d.*, c.name as city_name, c.country
FROM dealerships d
LEFT JOIN cities c ON c.id = d.city_id
WHERE d.id = 1;


-- Get all dealerships with city data (for dropdowns etc.)
SELECT d.id, d.name, c.name AS city_name, c.country, d.phone_number, d.email
FROM dealerships d
LEFT JOIN cities c ON c.id = d.city_id
WHERE d.is_active = true
ORDER BY c.country, c.name, d.name;


-- Update dealership phone number
UPDATE dealerships
SET phone_number = '+375291112233', updated_at = NOW()
WHERE id = 1;


-- Update dealership status (activate/deactivate)
UPDATE dealerships
SET is_active = false, updated_at = NOW()
WHERE id = 1;


-- Delete dealership by ID
DELETE FROM dealerships
WHERE id = 1;


-- Get dealerships by city
SELECT d.*, c.name as city_name, c.country
FROM dealerships d
LEFT JOIN cities c ON c.id = d.city_id
WHERE d.city_id = 1 AND d.is_active = true;


-- Get dealerships in specific country
SELECT d.*, c.name as city_name, c.country
FROM dealerships d
LEFT JOIN cities c ON c.id = d.city_id
WHERE c.country = 'Belarus' AND d.is_active = true;


-- Get vehicles available at specific dealership
SELECT v.*, m.name, b.name as body_type, e.name as engine_name, t.name as transmission_name
FROM vehicles v
LEFT JOIN models m ON m.id = v.model_id
LEFT JOIN body_types b ON b.id = m.body_type_id
LEFT JOIN engines e ON e.id = m.engine_id
LEFT JOIN transmissions t ON t.id = m.transmission_id
WHERE v.dealership_id = 1 AND v.is_active = true;


-- Get orders for specific dealership
SELECT o.*, c.id AS customer_id, u.first_name, u.second_name, u.email, v.vin, m.name as model_name
FROM orders o
LEFT JOIN customers c ON c.id = o.customer_id
LEFT JOIN users u ON u.id = c.user_id
LEFT JOIN vehicles v ON v.id = o.vehicle_id
LEFT JOIN models m ON m.id = v.model_id
WHERE o.dealership_id = 1;


-- Get custom orders for specific dealership
SELECT co.*, c.id as customer_id, u.first_name, u.second_name, u.email, m.name as model_name, e.name as engine_name, t.name as transmission_name
FROM custom_orders co
LEFT JOIN customers c ON c.id = co.customer_id
LEFT JOIN users u ON u.id = c.user_id
LEFT JOIN models m ON m.id = co.model_id
LEFT JOIN engines e ON e.id = co.engine_id
LEFT JOIN transmissions t ON t.id = co.transmission_id
WHERE co.dealership_id = 1;


-- Get test drive requests for specific dealership
SELECT tdr.*, c.id as customer_id, u.phone_number, v.vin, m.name as model_name, d.name as dealership_name
FROM test_drive_requests tdr
LEFT JOIN customers c ON c.id = tdr.customer_id
LEFT JOIN users u ON u.id = c.user_id
LEFT JOIN vehicles v ON v.id = tdr.vehicle_id
LEFT JOIN models m ON m.id = v.model_id
LEFT JOIN dealerships d ON d.id = tdr.dealership_id
WHERE tdr.dealership_id = 1;
