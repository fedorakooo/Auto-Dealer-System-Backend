-- Get active car model by UUID
SELECT
    id,
    body_type_id,
    engine_id,
    transmission_id,
    name,
    model_code,
    is_in_production,
    production_year_start,
    production_year_end,
    description,
    drive_type,
    max_speed_kmh,
    acceleration_0_100_sec,
    fuel_tank_capacity_l,
    number_of_seats,
    number_of_doors,
    length_mm,
    width_mm,
    height_mm,
    curb_weight_kg,
    gross_weight_kg,
    created_at,
    updated_at
FROM models
WHERE id = '2bb5382f-462d-42ac-8fb9-f223d0261941' AND is_in_production = true;


-- Get paginated active models by body type
SELECT
    id,
    body_type_id,
    engine_id,
    transmission_id,
    name,
    model_code,
    is_in_production,
    production_year_start,
    production_year_end,
    description,
    drive_type,
    number_of_seats,
    number_of_doors,
    created_at,
    updated_at
FROM models
WHERE body_type_id = 1 AND is_in_production = true
ORDER BY production_year_start DESC
OFFSET 0 LIMIT 20;


-- Get active models by production year range
SELECT
    id,
    body_type_id,
    engine_id,
    transmission_id,
    name,
    model_code,
    is_in_production,
    production_year_start,
    production_year_end,
    drive_type,
    max_speed_kmh,
    number_of_seats,
    number_of_doors
FROM models
WHERE production_year_start BETWEEN 2020 AND 2025 AND is_in_production = true
ORDER BY production_year_start DESC
OFFSET 0 LIMIT 20;


-- Count active models in a body type
SELECT COUNT(*)
FROM models
WHERE body_type_id = 1 AND is_in_production = true;


-- Insert new car model
INSERT INTO models (
    id,
    body_type_id,
    engine_id,
    transmission_id,
    name,
    model_code,
    is_in_production,
    production_year_start,
    production_year_end,
    description,
    drive_type,
    max_speed_kmh,
    acceleration_0_100_sec,
    fuel_tank_capacity_l,
    number_of_seats,
    number_of_doors,
    length_mm,
    width_mm,
    height_mm,
    curb_weight_kg,
    gross_weight_kg
) VALUES (
    '2bb5382f-462d-42ac-8fb9-f223d0261941',
    1,
    3,
    2,
    'Audi A6 Sedan 50 TDI quattro',
    '4K',
    TRUE,
    2024,
    NULL,
    'Luxury mid-size sedan with advanced diesel engine and quattro AWD',
    'AWD',
    250,
    5.6,
    65,
    5,
    4,
    4939,
    1886,
    1457,
    1820,
    2400
);


-- Update model description
UPDATE models
SET description = 'Updated Audi A6 Sedan 50 TDI quattro with enhanced infotainment and mild hybrid system'
WHERE id = '2bb5382f-462d-42ac-8fb9-f223d0261941';


-- Soft delete model
UPDATE models
SET is_in_production = false
WHERE id = '2bb5382f-462d-42ac-8fb9-f223d0261941';


-- Hard delete model
DELETE FROM models
WHERE id = '2bb5382f-462d-42ac-8fb9-f223d0261941';
