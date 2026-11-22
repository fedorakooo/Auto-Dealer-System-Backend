-- Vehicles are now addressed through their model (/models/{model_id}/vehicles).
-- 1. One filtered vehicle query serves both a model's stock (model_id, trim_id) and the cross-model search
--    (model name, body type, fuel, gearbox), so get_vehicles_filtered/count_vehicles_filtered gain those filters.
-- 2. get_model_stock_stats gives the catalog "N in stock, from X" per model.

DROP FUNCTION get_vehicles_filtered(UUID, INTEGER, vehicle_lifecycle_status, DECIMAL, DECIMAL, VARCHAR, VARCHAR, INTEGER, INTEGER);
DROP FUNCTION count_vehicles_filtered(UUID, INTEGER, vehicle_lifecycle_status, DECIMAL, DECIMAL);

CREATE FUNCTION get_vehicles_filtered(
    p_model_id UUID DEFAULT NULL,
    p_trim_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL,
    p_status vehicle_lifecycle_status DEFAULT NULL,
    p_min_price DECIMAL DEFAULT NULL,
    p_max_price DECIMAL DEFAULT NULL,
    p_model_name VARCHAR DEFAULT NULL,
    p_body_type VARCHAR DEFAULT NULL,
    p_fuel_type fuel_type DEFAULT NULL,
    p_transmission_type transmission_type DEFAULT NULL,
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
        JOIN models m ON m.id = v.model_id
        JOIN trims tr ON tr.id = v.trim_id
        JOIN body_types bt ON bt.id = m.body_type_id
        JOIN engines e ON e.id = tr.engine_id
        JOIN transmissions t ON t.id = tr.transmission_id
        WHERE ($1 IS NULL OR v.model_id = $1)
          AND ($2 IS NULL OR v.trim_id = $2)
          AND ($3 IS NULL OR v.dealership_id = $3)
          AND ($4 IS NULL OR v.status = $4)
          AND ($5 IS NULL OR v.price >= $5)
          AND ($6 IS NULL OR v.price <= $6)
          AND ($7 IS NULL OR m.name ILIKE ''%%'' || $7 || ''%%'')
          AND ($8 IS NULL OR bt.name ILIKE $8)
          AND ($9 IS NULL OR e.fuel_type = $9)
          AND ($10 IS NULL OR t.type = $10)
        ORDER BY v.%s, v.id
        OFFSET $11 LIMIT $12',
        v_order_by
    ) USING p_model_id, p_trim_id, p_dealership_id, p_status, p_min_price, p_max_price,
            p_model_name, p_body_type, p_fuel_type, p_transmission_type, p_offset, p_limit;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION count_vehicles_filtered(
    p_model_id UUID DEFAULT NULL,
    p_trim_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL,
    p_status vehicle_lifecycle_status DEFAULT NULL,
    p_min_price DECIMAL DEFAULT NULL,
    p_max_price DECIMAL DEFAULT NULL,
    p_model_name VARCHAR DEFAULT NULL,
    p_body_type VARCHAR DEFAULT NULL,
    p_fuel_type fuel_type DEFAULT NULL,
    p_transmission_type transmission_type DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM vehicles v
    JOIN models m ON m.id = v.model_id
    JOIN trims tr ON tr.id = v.trim_id
    JOIN body_types bt ON bt.id = m.body_type_id
    JOIN engines e ON e.id = tr.engine_id
    JOIN transmissions t ON t.id = tr.transmission_id
    WHERE (p_model_id IS NULL OR v.model_id = p_model_id)
      AND (p_trim_id IS NULL OR v.trim_id = p_trim_id)
      AND (p_dealership_id IS NULL OR v.dealership_id = p_dealership_id)
      AND (p_status IS NULL OR v.status = p_status)
      AND (p_min_price IS NULL OR v.price >= p_min_price)
      AND (p_max_price IS NULL OR v.price <= p_max_price)
      AND (p_model_name IS NULL OR m.name ILIKE '%' || p_model_name || '%')
      AND (p_body_type IS NULL OR bt.name ILIKE p_body_type)
      AND (p_fuel_type IS NULL OR e.fuel_type = p_fuel_type)
      AND (p_transmission_type IS NULL OR t.type = p_transmission_type);

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION get_model_stock_stats(p_model_ids UUID[])
RETURNS TABLE (
    model_id UUID,
    vehicles_in_stock INTEGER,
    min_price DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT v.model_id, COUNT(*)::INTEGER, MIN(v.price)
    FROM vehicles v
    WHERE v.model_id = ANY(p_model_ids)
      AND v.status = 'in_stock'
    GROUP BY v.model_id;
END;
$$ LANGUAGE plpgsql;
