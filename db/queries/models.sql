-- Get active car model by UUID
SELECT
    id,
    body_type_id,
    name,
    model_code,
    is_in_production,
    production_year_start,
    production_year_end,
    description,
    number_of_seats,
    number_of_doors,
    length_mm,
    width_mm,
    height_mm,
    created_at,
    updated_at
FROM models
WHERE id = '2bb5382f-462d-42ac-8fb9-f223d0261941' AND is_in_production = true;


-- Get all trims (engine, gearbox, drive) of a model
SELECT tr.id, tr.name, e.name AS engine_name, e.fuel_type, t.name AS transmission_name, tr.drive_type,
       tr.max_speed_kmh, tr.acceleration_0_100_sec, tr.fuel_tank_capacity_l, tr.curb_weight_kg, tr.gross_weight_kg
FROM trims tr
JOIN engines e ON e.id = tr.engine_id
JOIN transmissions t ON t.id = tr.transmission_id
WHERE tr.model_id = '2bb5382f-462d-42ac-8fb9-f223d0261941'
ORDER BY tr.name;


-- Get models that are offered with a given engine
SELECT m.id, m.name, tr.name AS trim_name
FROM models m
JOIN trims tr ON tr.model_id = m.id
WHERE tr.engine_id = 2
ORDER BY m.name, tr.name;


-- Get paginated active models by body type
SELECT
    id,
    body_type_id,
    name,
    model_code,
    is_in_production,
    production_year_start,
    production_year_end,
    description,
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
    name,
    model_code,
    is_in_production,
    production_year_start,
    production_year_end,
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


-- Insert new car model with one trim
INSERT INTO models (
    id,
    body_type_id,
    name,
    model_code,
    is_in_production,
    production_year_start,
    production_year_end,
    description,
    number_of_seats,
    number_of_doors,
    length_mm,
    width_mm,
    height_mm
) VALUES (
    '3d1a9f0e-5f0b-4f3a-9a53-2c1d6a4b7e10',
    1,
    'A6 Sedan',
    '4K',
    TRUE,
    2024,
    NULL,
    'Luxury mid-size sedan',
    5,
    4,
    4939,
    1886,
    1457
);

INSERT INTO trims (
    model_id,
    name,
    engine_id,
    transmission_id,
    drive_type,
    max_speed_kmh,
    acceleration_0_100_sec,
    fuel_tank_capacity_l,
    curb_weight_kg,
    gross_weight_kg
) VALUES (
    '3d1a9f0e-5f0b-4f3a-9a53-2c1d6a4b7e10',
    '50 TDI quattro',
    5,
    2,
    'AWD',
    250,
    5.6,
    65,
    1820,
    2400
);


-- Update model description
UPDATE models
SET description = 'Updated Audi A6 Sedan with enhanced infotainment and mild hybrid system'
WHERE id = '3d1a9f0e-5f0b-4f3a-9a53-2c1d6a4b7e10';


-- Soft delete model
UPDATE models
SET is_in_production = false
WHERE id = '3d1a9f0e-5f0b-4f3a-9a53-2c1d6a4b7e10';


-- Hard delete model (its trims go with it; fails while vehicles or custom orders use them)
DELETE FROM models
WHERE id = '3d1a9f0e-5f0b-4f3a-9a53-2c1d6a4b7e10';
