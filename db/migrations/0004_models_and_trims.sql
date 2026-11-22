-- A model is a body/line (A4 Sedan); a trim is a sellable configuration of it (45 TFSI: engine, gearbox, drive).
-- Vehicles and custom orders reference a trim; model_id stays next to trim_id and the composite FK keeps them consistent.

CREATE TABLE trims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    engine_id INTEGER NOT NULL REFERENCES engines(id),
    transmission_id INTEGER NOT NULL REFERENCES transmissions(id),
    drive_type drive_type,
    max_speed_kmh INTEGER CHECK (max_speed_kmh > 0),
    acceleration_0_100_sec DECIMAL(3, 1) CHECK (acceleration_0_100_sec > 0),
    fuel_tank_capacity_l INTEGER CHECK (fuel_tank_capacity_l > 0),
    curb_weight_kg INTEGER CHECK (curb_weight_kg > 0),
    gross_weight_kg INTEGER CHECK (gross_weight_kg > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    UNIQUE (model_id, name),
    UNIQUE (id, model_id)
);

CREATE INDEX idx_trims_model_id ON trims(model_id);
CREATE INDEX idx_trims_engine_id ON trims(engine_id);
CREATE INDEX idx_trims_transmission_id ON trims(transmission_id);
CREATE TRIGGER trg_trims_updated_at BEFORE UPDATE ON trims FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- 1. Every existing model becomes one model + one trim named after its engine.
INSERT INTO trims (model_id, name, engine_id, transmission_id, drive_type, max_speed_kmh,
                   acceleration_0_100_sec, fuel_tank_capacity_l, curb_weight_kg, gross_weight_kg)
SELECT m.id, e.name, m.engine_id, m.transmission_id, m.drive_type, m.max_speed_kmh,
       m.acceleration_0_100_sec, m.fuel_tank_capacity_l, m.curb_weight_kg, m.gross_weight_kg
FROM models m
JOIN engines e ON e.id = m.engine_id;

-- Custom orders may have asked for an engine/gearbox pair the model never had: keep it as an extra trim.
INSERT INTO trims (model_id, name, engine_id, transmission_id, drive_type)
SELECT DISTINCT co.model_id,
       format('%s / %s (%s-%s)', e.name, t.name, co.engine_id, co.transmission_id),
       co.engine_id, co.transmission_id, m.drive_type
FROM custom_orders co
JOIN models m ON m.id = co.model_id
JOIN engines e ON e.id = co.engine_id
JOIN transmissions t ON t.id = co.transmission_id
WHERE NOT EXISTS (
    SELECT 1 FROM trims tr
    WHERE tr.model_id = co.model_id AND tr.engine_id = co.engine_id AND tr.transmission_id = co.transmission_id
);


-- 2. vehicles.trim_id
ALTER TABLE vehicles ADD COLUMN trim_id UUID;
ALTER TABLE vehicles DISABLE TRIGGER trg_vehicles_updated_at;
UPDATE vehicles v
SET trim_id = (
    SELECT tr.id FROM trims tr WHERE tr.model_id = v.model_id ORDER BY (tr.name LIKE '% / %'), tr.id LIMIT 1
);
ALTER TABLE vehicles ENABLE TRIGGER trg_vehicles_updated_at;
ALTER TABLE vehicles ALTER COLUMN trim_id SET NOT NULL;
ALTER TABLE vehicles ADD CONSTRAINT fk_vehicles_trim_model
    FOREIGN KEY (trim_id, model_id) REFERENCES trims(id, model_id);
CREATE INDEX idx_vehicles_trim_id ON vehicles(trim_id);


-- 3. custom_orders.trim_id replaces engine_id + transmission_id
ALTER TABLE custom_orders ADD COLUMN trim_id UUID;
ALTER TABLE custom_orders DISABLE TRIGGER trg_custom_orders_updated_at;
UPDATE custom_orders co
SET trim_id = (
    SELECT tr.id FROM trims tr
    WHERE tr.model_id = co.model_id AND tr.engine_id = co.engine_id AND tr.transmission_id = co.transmission_id
    ORDER BY (tr.name LIKE '% / %'), tr.id LIMIT 1
);
ALTER TABLE custom_orders ENABLE TRIGGER trg_custom_orders_updated_at;
ALTER TABLE custom_orders ALTER COLUMN trim_id SET NOT NULL;
ALTER TABLE custom_orders DROP COLUMN engine_id;
ALTER TABLE custom_orders DROP COLUMN transmission_id;
ALTER TABLE custom_orders ADD CONSTRAINT fk_custom_orders_trim_model
    FOREIGN KEY (trim_id, model_id) REFERENCES trims(id, model_id);
CREATE INDEX idx_custom_orders_trim_id ON custom_orders(trim_id);


-- 4. models keep only what is shared by every trim
ALTER TABLE models DROP COLUMN engine_id;
ALTER TABLE models DROP COLUMN transmission_id;
ALTER TABLE models DROP COLUMN drive_type;
ALTER TABLE models DROP COLUMN max_speed_kmh;
ALTER TABLE models DROP COLUMN acceleration_0_100_sec;
ALTER TABLE models DROP COLUMN fuel_tank_capacity_l;
ALTER TABLE models DROP COLUMN curb_weight_kg;
ALTER TABLE models DROP COLUMN gross_weight_kg;


-- 5. Functions that read the moved columns
DROP FUNCTION get_models_filtered(VARCHAR, BOOLEAN, INTEGER, INTEGER, VARCHAR, VARCHAR, INTEGER, INTEGER);

CREATE FUNCTION get_models_filtered(
    p_name VARCHAR DEFAULT NULL,
    p_is_in_production BOOLEAN DEFAULT NULL,
    p_body_type_id INTEGER DEFAULT NULL,
    p_engine_id INTEGER DEFAULT NULL,
    p_sort_by VARCHAR DEFAULT 'created_at',
    p_order_direction VARCHAR DEFAULT 'ASC',
    p_offset INTEGER DEFAULT 0,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    body_type_id INTEGER,
    name VARCHAR,
    model_code VARCHAR,
    is_in_production BOOLEAN,
    production_year_start INTEGER,
    production_year_end INTEGER,
    description TEXT,
    number_of_seats INTEGER,
    number_of_doors INTEGER,
    length_mm INTEGER,
    width_mm INTEGER,
    height_mm INTEGER,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) AS $$
DECLARE
    v_order_by TEXT;
BEGIN
    v_order_by := CASE
        WHEN p_sort_by IN ('created_at', 'name', 'production_year_start') THEN p_sort_by
        ELSE 'created_at'
    END;

    IF UPPER(p_order_direction) NOT IN ('ASC', 'DESC') THEN
        v_order_by := v_order_by || ' ASC';
    ELSE
        v_order_by := v_order_by || ' ' || UPPER(p_order_direction);
    END IF;

    RETURN QUERY
    EXECUTE format('
        SELECT
            m.id,
            m.body_type_id,
            m.name,
            m.model_code,
            m.is_in_production,
            m.production_year_start,
            m.production_year_end,
            m.description,
            m.number_of_seats,
            m.number_of_doors,
            m.length_mm,
            m.width_mm,
            m.height_mm,
            m.created_at,
            m.updated_at
        FROM models m
        WHERE ($1 IS NULL OR m.name ILIKE ''%%'' || $1 || ''%%'')
          AND ($2 IS NULL OR m.is_in_production = $2)
          AND ($3 IS NULL OR m.body_type_id = $3)
          AND ($4 IS NULL OR EXISTS (SELECT 1 FROM trims tr WHERE tr.model_id = m.id AND tr.engine_id = $4))
        ORDER BY m.%s, m.id
        OFFSET $5 LIMIT $6',
        v_order_by
    ) USING p_name, p_is_in_production, p_body_type_id, p_engine_id, p_offset, p_limit;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION count_models_filtered(
    p_name VARCHAR DEFAULT NULL,
    p_is_in_production BOOLEAN DEFAULT NULL,
    p_body_type_id INTEGER DEFAULT NULL,
    p_engine_id INTEGER DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM models m
    WHERE (p_name IS NULL OR m.name ILIKE '%' || p_name || '%')
      AND (p_is_in_production IS NULL OR m.is_in_production = p_is_in_production)
      AND (p_body_type_id IS NULL OR m.body_type_id = p_body_type_id)
      AND (p_engine_id IS NULL OR EXISTS (SELECT 1 FROM trims tr WHERE tr.model_id = m.id AND tr.engine_id = p_engine_id));

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION get_vehicle_with_details(UUID, VARCHAR);
DROP FUNCTION get_vehicles_filtered(UUID, INTEGER, vehicle_lifecycle_status, DECIMAL, DECIMAL, VARCHAR, VARCHAR, INTEGER, INTEGER);

CREATE FUNCTION get_vehicle_with_details(p_vehicle_id UUID DEFAULT NULL, p_vin VARCHAR DEFAULT NULL)
RETURNS TABLE (
    id UUID,
    model_id UUID,
    trim_id UUID,
    dealership_id INTEGER,
    vin VARCHAR,
    production_year INTEGER,
    exterior_color VARCHAR,
    interior_color VARCHAR,
    price DECIMAL,
    status vehicle_lifecycle_status,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    model_name VARCHAR,
    trim_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.id,
        v.model_id,
        v.trim_id,
        v.dealership_id,
        v.vin,
        v.production_year,
        v.exterior_color,
        v.interior_color,
        v.price,
        v.status,
        v.created_at,
        v.updated_at,
        m.name AS model_name,
        tr.name AS trim_name
    FROM vehicles v
    LEFT JOIN models m ON m.id = v.model_id
    LEFT JOIN trims tr ON tr.id = v.trim_id
    WHERE (p_vehicle_id IS NULL OR v.id = p_vehicle_id)
      AND (p_vin IS NULL OR v.vin = p_vin)
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION get_vehicles_filtered(
    p_model_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL,
    p_status vehicle_lifecycle_status DEFAULT NULL,
    p_min_price DECIMAL DEFAULT NULL,
    p_max_price DECIMAL DEFAULT NULL,
    p_sort_by VARCHAR DEFAULT 'created_at',
    p_order_direction VARCHAR DEFAULT 'ASC',
    p_offset INTEGER DEFAULT 0,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    model_id UUID,
    trim_id UUID,
    dealership_id INTEGER,
    vin VARCHAR,
    production_year INTEGER,
    exterior_color VARCHAR,
    interior_color VARCHAR,
    price DECIMAL,
    status vehicle_lifecycle_status,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    model_name VARCHAR,
    trim_name VARCHAR
) AS $$
DECLARE
    v_order_by TEXT;
BEGIN
    v_order_by := CASE
        WHEN p_sort_by IN ('created_at', 'price', 'production_year') THEN p_sort_by
        ELSE 'created_at'
    END;

    IF UPPER(p_order_direction) NOT IN ('ASC', 'DESC') THEN
        v_order_by := v_order_by || ' ASC';
    ELSE
        v_order_by := v_order_by || ' ' || UPPER(p_order_direction);
    END IF;

    RETURN QUERY
    EXECUTE format('
        SELECT
            v.id,
            v.model_id,
            v.trim_id,
            v.dealership_id,
            v.vin,
            v.production_year,
            v.exterior_color,
            v.interior_color,
            v.price,
            v.status,
            v.created_at,
            v.updated_at,
            m.name AS model_name,
            tr.name AS trim_name
        FROM vehicles v
        LEFT JOIN models m ON m.id = v.model_id
        LEFT JOIN trims tr ON tr.id = v.trim_id
        WHERE ($1 IS NULL OR v.model_id = $1)
          AND ($2 IS NULL OR v.dealership_id = $2)
          AND ($3 IS NULL OR v.status = $3)
          AND ($4 IS NULL OR v.price >= $4)
          AND ($5 IS NULL OR v.price <= $5)
        ORDER BY v.%s, v.id
        OFFSET $6 LIMIT $7',
        v_order_by
    ) USING p_model_id, p_dealership_id, p_status, p_min_price, p_max_price, p_offset, p_limit;
END;
$$ LANGUAGE plpgsql;

-- Same signature and result as before; engine, gearbox and drive now come from the vehicle's trim.
CREATE OR REPLACE FUNCTION search_vehicles(
    p_model_name VARCHAR DEFAULT NULL,
    p_body_type VARCHAR DEFAULT NULL,
    p_fuel_type fuel_type DEFAULT NULL,
    p_transmission_type transmission_type DEFAULT NULL,
    p_min_price DECIMAL DEFAULT 0,
    p_max_price DECIMAL DEFAULT 99999999,
    p_dealership_id INTEGER DEFAULT NULL
) RETURNS TABLE (
    vehicle_id UUID,
    model_name VARCHAR,
    body_type VARCHAR,
    fuel_type fuel_type,
    transmission_type transmission_type,
    exterior_color VARCHAR,
    price DECIMAL(12,2),
    dealership_name VARCHAR,
    city_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.id,
        m.name,
        bt.name,
        e.fuel_type,
        t.type,
        v.exterior_color,
        v.price,
        d.name,
        c.name
    FROM vehicles v
    JOIN models m ON v.model_id = m.id
    JOIN trims tr ON tr.id = v.trim_id
    JOIN body_types bt ON m.body_type_id = bt.id
    JOIN engines e ON tr.engine_id = e.id
    JOIN transmissions t ON tr.transmission_id = t.id
    JOIN dealerships d ON v.dealership_id = d.id
    JOIN cities c ON d.city_id = c.id
    WHERE v.status = 'in_stock'
      AND v.price BETWEEN p_min_price AND p_max_price
      AND (p_model_name IS NULL OR m.name ILIKE '%' || p_model_name || '%')
      AND (p_body_type IS NULL OR bt.name = p_body_type)
      AND (p_fuel_type IS NULL OR e.fuel_type = p_fuel_type)
      AND (p_transmission_type IS NULL OR t.type = p_transmission_type)
      AND (p_dealership_id IS NULL OR v.dealership_id = p_dealership_id)
    ORDER BY v.price;
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION get_custom_order_with_details(UUID, INTEGER);

CREATE FUNCTION get_custom_order_with_details(
    p_custom_order_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    customer_id UUID,
    dealership_id INTEGER,
    model_id UUID,
    trim_id UUID,
    exterior_color VARCHAR,
    interior_color VARCHAR,
    status custom_order_status,
    estimated_price DECIMAL,
    final_price DECIMAL,
    notes TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    customer_first_name VARCHAR,
    customer_second_name VARCHAR,
    customer_email VARCHAR,
    model_name VARCHAR,
    trim_name VARCHAR,
    engine_name VARCHAR,
    transmission_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        co.id,
        co.customer_id,
        co.dealership_id,
        co.model_id,
        co.trim_id,
        co.exterior_color,
        co.interior_color,
        co.status,
        co.estimated_price,
        co.final_price,
        co.notes,
        co.created_at,
        co.updated_at,
        u.first_name AS customer_first_name,
        u.second_name AS customer_second_name,
        u.email AS customer_email,
        m.name AS model_name,
        tr.name AS trim_name,
        e.name AS engine_name,
        t.name AS transmission_name
    FROM custom_orders co
    LEFT JOIN customers c ON c.id = co.customer_id
    LEFT JOIN users u ON u.id = c.user_id
    LEFT JOIN models m ON m.id = co.model_id
    LEFT JOIN trims tr ON tr.id = co.trim_id
    LEFT JOIN engines e ON e.id = tr.engine_id
    LEFT JOIN transmissions t ON t.id = tr.transmission_id
    WHERE (p_custom_order_id IS NULL OR co.id = p_custom_order_id)
      AND (p_dealership_id IS NULL OR co.dealership_id = p_dealership_id);
END;
$$ LANGUAGE plpgsql;
